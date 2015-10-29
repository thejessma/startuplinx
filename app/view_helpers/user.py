from datetime import datetime
import json
from flask import session, url_for
import time
import urllib 
import urllib2
from sets import Set
import string
import random

from app.view_helpers.company import scrape_companies, \
        gen_fake_linkedin_id
from app.models import User, Company, Position, Education, School
from app.api_helpers.linkedin import get_current_linkedin_user, fetch_current_linkedin_user_data, fetch_current_linkedin_user_connections_data

IMAGE_SCRAPER_URL = 'http://54.172.148.221:5000/scrape_user_images'

def get_current_user():
    if 'user_id' not in session:
        return None
    user_id = session['user_id']
    user = User.query.get(user_id)
    return user

def populate_position_with_linkedin_data(position, position_data):
    position.linkedin_id = str(position_data['id'])
    if 'title' in position_data:
        position.title = position_data['title'].encode('utf8')
    if 'summary' in position_data:
        position.summary = position_data['summary'].encode('utf8')
    position.is_current = position_data['isCurrent']
    if 'startDate' in position_data:
        start_year = int(position_data['startDate']['year'])
        start_month = int(position_data['startDate']['month']) if 'month' in position_data['startDate'] else 1
        position.start_date = datetime(start_year, start_month, 1)
    if 'endDate' in position_data:
        end_year = int(position_data['endDate']['year'])
        end_month = int(position_data['endDate']['month']) if 'month' in position_data['endDate'] else 1
        position.end_date = datetime(end_year, end_month, 1)

def populate_education_with_linkedin_data(education, education_data):
    education.linkedin_id = str(education_data['id'])
    if 'degree' in education_data:
        education.degree = education_data['degree'].encode('utf8')
    if 'fieldOfStudy' in education_data:
        education.field_of_study = education_data['fieldOfStudy']
    if 'activities' in education_data:
        education.activities = education_data['activities']
    if 'startDate' in education_data:
        start_year = int(education_data['startDate']['year'])
        start_month = int(education_data['startDate']['month']) if 'month' in education_data['startDate'] else 1
        education.start_date = datetime(start_year, start_month, 1)
    if 'endDate' in education_data:
        end_year = int(education_data['endDate']['year'])
        end_month = int(education_data['endDate']['month']) if 'month' in education_data['endDate'] else 1
        education.end_date = datetime(end_year, end_month, 1)

def populate_user_with_linkedin_data(user, user_data, companies_info, positions, schools_info, educations, indirect=False):
    user.linkedin_id = user_data['id']
    if 'emailAddress' in user_data:
        user.email = user_data['emailAddress'].encode('utf8')
    if 'firstName' in user_data:
        user.first_name = user_data['firstName'].encode('utf8')
    if 'lastName' in user_data:
        user.last_name = user_data['lastName'].encode('utf8')
    user.name = user.first_name + ' ' + user.last_name
    #print user.name
    if 'headline' in user_data:
        user.headline = user_data['headline'].encode('utf8')
    user.picture_url = user_data.get('pictureUrl')
    if 'siteStandardProfileRequest' in user_data:
        user.linkedin_url = user_data['siteStandardProfileRequest']['url']
    if not indirect:
        user.last_linkedin_update = datetime.utcnow()

    if 'positions' in user_data and 'values' in user_data['positions']:
        for position_data in user_data['positions']['values']:
            position = Position()
            populate_position_with_linkedin_data(position, position_data)
            if not indirect:
                position.last_linkedin_update = datetime.utcnow()
            if position_data['company'].get('id'):
                # if the company exists, use its linkedin id to find it later
                company_linkedin_id = str(position_data['company'].get('id')) # important! convert to string
            else:
                # otherwise, generate a fake id
                company_linkedin_id = gen_fake_linkedin_id()
            company_name = position_data['company'].get('name')
            # TODO make it more intelligent -- but for now some companies don't have company_name... WTF linkedin...
            if company_linkedin_id and company_name:
                companies_info.append({
                    'name': company_name,
                    'linkedin_id': company_linkedin_id
                    })
            positions.append((position, company_linkedin_id, user.linkedin_id))

    if 'educations' in user_data and 'values' in user_data['educations']:
        for education_data in user_data['educations']['values']:
            education = Education()
            populate_education_with_linkedin_data(education, education_data)
            if not indirect:
                education.last_linkedin_update = datetime.utcnow()
            school_name = education_data.get('schoolName')
            school_identifier = school_name.lower() if school_name else None # we don't have linkedin id's like we do for companies -> cross-reference by name
            if school_name:
                schools_info.append({
                    'name': school_name,
                    'identifier': school_identifier
                    })
            educations.append((education, school_identifier, user.linkedin_id))
           
# this is almost the same as the one below -- change both at the same time
#
def insert_new_companies_and_positions(db, companies_info, positions, existing_connections_by_linkedin_ids, new_connections_by_linkedin_ids, current_user):
    # Step 3: Add companies
    #
    print 'step 7: get existing companies'
    start = time.time()
    companies_linkedin_ids = [x['linkedin_id'] for x in companies_info]
    q = Company.query.with_entities(Company.id, Company.linkedin_id, Company.name).filter(Company.linkedin_id.in_(companies_linkedin_ids))
    existing_companies = q.all()
    print 'It took ' + str(time.time() - start)
    print 'step 7.1: iterate over them'
    existing_companies_by_linkedin_ids = {c.linkedin_id: c for c in existing_companies}
    new_companies_by_linkedin_ids = dict()
    print 'step 8: add new ones'
    for company_info in companies_info:
        if str(company_info['linkedin_id']) not in existing_companies_by_linkedin_ids and str(company_info['linkedin_id']) not in new_companies_by_linkedin_ids:
            # Create hollow company and add it for scraping
            company = Company(company_info['linkedin_id'], company_info['name'])
            print 'name --> ' + company.name.encode('utf-8') + ', ' + str(company.linkedin_id)
            new_companies_by_linkedin_ids[company.linkedin_id] = company
            db.session.add(company)

    # Step 4: Get existing positions before flushing
    #
    print 'step 9: get existing positions'
    start = time.time()
    positions_linkedin_ids = [x[0].linkedin_id for x in positions]
    q = Position.query.with_entities(Position.id, Position.linkedin_id, Position.user_id).filter(Position.linkedin_id.in_(positions_linkedin_ids))
    existing_positions = q.all()
    print 'It took ' + str(time.time() - start)
    print 'step 9.1: iterate over them'
    existing_positions_linkedin_ids = Set([p.linkedin_id for p in existing_positions])

    # Step 5: Flush and prepare for scraping
    #
    print 'step 10: flush and prepare companies for scraping'
    start = time.time()
    db.session.flush()
    print 'It took ' + str(time.time() - start)
    new_companies_data = []
    for company_linkedin_id, company in new_companies_by_linkedin_ids.iteritems():
        if company.name and company.linkedin_id:
            #print 'SCRAPE ' + str(company.name.encode('utf8')) + ', ' + str(company.linkedin_id) + ', ' + str(company.id)
            new_companies_data.append({
                'name': company.name,
                'linkedin_id': company.linkedin_id,
                'callback_url': url_for('endpoints_bp.scraper_callback', company_id=company.id, _external=True)})

    # Step 6: Add positions -- must have flushed by this point to get company and user id's
    #
    print 'step 11: pair positions with companies, new and old'
    for position, company_linkedin_id, user_linkedin_id in positions:
        if position.linkedin_id in existing_positions_linkedin_ids:
            print 'FUCK'
            position.user_id = None
            continue
        if not company_linkedin_id or company_linkedin_id == 'None':
            print 'WHAT THE FUCK'
            continue
        company = existing_companies_by_linkedin_ids.get(company_linkedin_id) or new_companies_by_linkedin_ids.get(company_linkedin_id)
        if not company:
            print 'NOOOO'
            continue
        if not user_linkedin_id:
            print 'WTFFFFFFFF'
            continue
        user = existing_connections_by_linkedin_ids.get(user_linkedin_id) or new_connections_by_linkedin_ids.get(user_linkedin_id) or current_user
        if not user or user.linkedin_id != user_linkedin_id:
            print 'BLABLABLALBALB'
            continue
        print '  position ' + str(position.title) + ' -- c = ' + str(company.id) + '; u id = ' + str(user.id)
        position.company_id = company.id
        position.user_id = user.id
        db.session.add(position)

    return new_companies_data

# this is almost the same as the one above -- change both at the same time
#
def insert_new_schools_and_educations(db, schools_info, educations, existing_connections_by_linkedin_ids, new_connections_by_linkedin_ids, current_user):
    # Step 3-B: Add schools 
    #
    print 'step 7-B: get existing schools'
    start = time.time()
    schools_identifiers = [x['identifier'] for x in schools_info]
    q = School.query.with_entities(School.id, School.identifier, School.name).filter(School.identifier.in_(schools_identifiers))
    existing_schools = q.all()
    print 'B-It took ' + str(time.time() - start)
    print 'step 7-B.1: iterate over them'
    existing_schools_by_identifiers = {c.identifier: c for c in existing_schools}
    new_schools_by_identifiers = dict()
    print 'step 8-B: add new ones'
    for school_info in schools_info:
        if school_info['identifier'] not in existing_schools_by_identifiers and school_info['identifier'] not in new_schools_by_identifiers:
            # Create hollow school and add it for scraping
            school = School(school_info['identifier'], school_info['name'])
            #print 'name --> ' + school.name.encode('utf-8') + ', ' + str(school.identifier) TODO this throws ASCII / unicode error... wtf
            new_schools_by_identifiers[school.identifier] = school
            db.session.add(school)

    # Step 4-B: Get existing educations 
    #
    print 'step 9-B: get existing educations'
    start = time.time()
    educations_linkedin_ids = [x[0].linkedin_id for x in educations]
    q = Education.query.with_entities(Education.id, Education.linkedin_id, Education.user_id).filter(Education.linkedin_id.in_(educations_linkedin_ids))
    existing_educations = q.all()
    print 'B-It took ' + str(time.time() - start)
    print 'step 9-B.1: iterate over them'
    existing_educations_linkedin_ids = Set([e.linkedin_id for e in existing_educations])

    # Step 5-B: Flush and prepare for scraping
    #
    print 'step 10-B: flush and prepare schools for scraping'
    start = time.time()
    db.session.flush()
    print 'B-It took ' + str(time.time() - start)
    new_schools_data = []
    for school_identifier, school in new_schools_by_identifiers.iteritems():
        if school.name and school.linkedin_id:
            #print 'SCRAPE ' + str(school.name.encode('utf8')) + ', ' + str(school.identifier) + ', ' + str(school.id)
            new_schools_data.append({
                'name': school.name,
                'identifier': school.identifier,
                'callback_url': None}) # TODO scrape at some point...

    # Step 6-B: Add educations -- must have flushed by this point to get school and user id's
    #
    print 'step 11-B: pair educations with schools, new and old'
    for education, school_identifier, user_linkedin_id in educations:
        if education.linkedin_id in existing_educations_linkedin_ids:
            print 'FUCK'
            education.user_id = None
            continue
        if not school_identifier or school_identifier == 'None':
            print 'WHAT THE FUCK'
            continue
        school = existing_schools_by_identifiers.get(school_identifier) or new_schools_by_identifiers.get(school_identifier)
        if not school:
            print 'NOOOO'
            continue
        if not user_linkedin_id:
            print 'WTFFFFFFFF'
            continue
        user = existing_connections_by_linkedin_ids.get(user_linkedin_id) or new_connections_by_linkedin_ids.get(user_linkedin_id) or current_user
        if not user or user.linkedin_id != user_linkedin_id:
            print 'BLABLABLALBALB'
            continue
        print '   education ' + str(education.degree) + ' -- c = ' + str(school.id) + '; u id = ' + str(user.id)
        education.school_id = school.id
        education.user_id = user.id
        db.session.add(education)

    return new_schools_data

# Assumes the user exists as a hollow user with the linkedin_id
#
def fetch_and_populate_current_user_from_linkedin(db):
    companies_info = [] # companies from user and all connections' positions accumulate here
    positions = [] # positions from user and all connections accumulate here
    schools_info = [] # schools from user 
    educations = [] # educations from user
    db.session.autoflush = False

    current_user = get_current_linkedin_user()
    if not current_user:
        return None

    # We have a few things to insert:
    # user, connections, friendships, companies, flush, positions, send companies for scraping
    # We need to do it in order

    # Step 1: Fetch user linkedin data and populare user fields (user already inserted)
    #
    print 'step 1: fetch user linkedin data'
    user_data = fetch_current_linkedin_user_data()
    print 'step 2: populate user'
    populate_user_with_linkedin_data(current_user, user_data, companies_info, positions, schools_info, educations)

    # Step 2: Fetch her connections, populate them and insert them, also add friendships
    #
    print 'step 3: fetch connections data'
    connections_data = fetch_current_linkedin_user_connections_data() 
    print 'step 4: get existing connections '
    if 'values' not in connections_data:
        connections_data['values'] = []
    connections_linkedin_ids = [x['id'] for x in connections_data['values']]
    existing_connections = User.query.filter(User.linkedin_id.in_(connections_linkedin_ids)).all()
    existing_connections_by_linkedin_ids = {u.linkedin_id: u for u in existing_connections}
    new_connections_by_linkedin_ids = dict()
    print 'step 6: add the new ones'
    for connection_data in connections_data['values']:
        if connection_data['id'] not in existing_connections_by_linkedin_ids:
            if connection_data['id'] == 'private':
                continue
            connection = User(connection_data['id'])
            populate_user_with_linkedin_data(connection, connection_data, companies_info, positions, schools_info, educations, indirect=True)
            new_connections_by_linkedin_ids[connection.linkedin_id] = connection
            db.session.add(connection)
            current_user.friends.append(connection)
    print 'step 6.1: add friendships with existing users'
    for connection in existing_connections:
        current_user.friends.append(connection)

    new_companies_data = insert_new_companies_and_positions(db, companies_info, positions, existing_connections_by_linkedin_ids, new_connections_by_linkedin_ids, current_user)
    new_schools_data = insert_new_schools_and_educations(db, schools_info, educations, existing_connections_by_linkedin_ids, new_connections_by_linkedin_ids, current_user)

    print 'step 12: commit'
    current_user.is_registered = True
    db.session.commit()

    print 'step 13: send companies for scraping'
    scrape_companies(new_companies_data)
    print 'step 13-B: send schools for scraping'
    #scrape_schools(new_schools_data) TODO implelent...at some point

    print 'step 14: DONE!'
    return current_user


def scrape_user_images(users_info):
    print ' sending ' + str(len(users_info)) + ' user IMAGES for scraping...'
    data = urllib.urlencode({'data': json.dumps(users_info)})
    req = urllib2.Request(IMAGE_SCRAPER_URL, data)
    resp = urllib2.urlopen(req)
    resp_html = resp.read()
    print ' response was ' + str(resp_html)

def rescrape_user_images_from_list(users):
    users_info = []
    for user in users:
        user_info = {
            'picture_url': user.picture_url,
            'user_id': user.id,
            'name': user.name,
            'linkedin_id': user.linkedin_id,
            'callback_url': url_for('endpoints_bp.user_image_scraper_callback', user_id=user.id, _external=True)}
        users_info.append(user_info)
    scrape_user_images(users_info)

