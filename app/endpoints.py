from flask import Blueprint, session, redirect, url_for
import json
from flask import request 
from sqlalchemy import desc
import time

from models import db, create_db, User, Company, Feedback
from api_helpers.linkedin import get_current_linkedin_user, \
        get_linkedin_id, \
        post_linkedin_message
from view_helpers.company import rescrape_companies_from_list, \
        SUPPORTED_FIELDS, \
        DEFAULT_RESCRAPE_MODE, \
        SOFT_RESCRAPE_MODE, \
        FROM_URL_RESCRAPE_MODE, \
        merge_companies_query_template, \
        gen_fake_linkedin_id
from view_helpers.user import get_current_user, \
        rescrape_user_images_from_list
from logging import log_event
from decorators import admin_only

endpoints_bp = Blueprint('endpoints_bp', __name__)

@endpoints_bp.route('/wait_for_register', methods=['POST', 'GET'])
def wait_for_register():
    user = get_current_linkedin_user()
    print 'Current linkedin id' + str(get_linkedin_id())
    if not user:
        return "Not authenticated"
    times_left = 100
    while not user.is_registered and times_left >= 0:
        times_left -= 1 # this is to make sure this doesn't become an infinite loop
        time.sleep(5)
        db.session.commit() # Retarded way to start a new transaction because FUCK sqlalchemy...
        user = get_current_linkedin_user()
        print ' is registered? ' + str(user.linkedin_id) + '  name ' + str(user.name) + ' ----> ' + str(user.is_registered)
    time.sleep(5) # so some startups can load in the feed
    resp = json.dumps({'is_registered': user.is_registered})
    print 'wait_for_register is about to return a response = ' + str(resp)
    return resp 

@endpoints_bp.route('/scraper_callback/<company_id>', methods=['POST', 'GET'])
def scraper_callback(company_id):
    company = Company.query.get(company_id)
    print 'scraper callback! for ' + str(company.id) + ', ' + company.name.encode('utf8') + ', ' + str(company.linkedin_id)
    company_data = json.loads(request.values.get('data'))
    if company_data.get('do_erase_current_field_values'):
        company.clear_fields(SUPPORTED_FIELDS)
    company.deserialize_fields(SUPPORTED_FIELDS, company_data)
    company.remote_id = company_data.get('remote_id')
    company.is_feed_ready = True
    db.session.commit()
    return 'YAY' # TODO normal return 

@endpoints_bp.route('/user_image_scraper_callback/<user_id>', methods=['POST', 'GET'])
def user_image_scraper_callback(user_id):
    user = User.query.get(user_id)
    print 'user image scraper callback! for ' + str(user.id) + ', ' + user.name.encode('utf8') + ', ' + str(user.linkedin_id)
    user_info = json.loads(request.values.get('data'))
    user.local_picture_url = user_info['local_picture_url']
    db.session.commit()
    return 'YaaY' # TODO normal return 

@endpoints_bp.route('/add_favorite/<company_id>', methods=['POST', 'GET'])
def add_favorite(company_id):
    current_user = get_current_user()
    if not current_user:
        return 'BLA' # TODO better response
    company = Company.query.get(company_id)
    if not company:
        return 'BLAA' # TODO better
    current_user.favorites.append(company)
    db.session.commit()
    resp = json.dumps({'status': 'ok', 'company_id': company_id})
    print 'add favorite response = ' + str(resp)
    return resp # TODO better response

@endpoints_bp.route('/remove_favorite/<company_id>', methods=['POST', 'GET'])
def remove_favorite(company_id):
    current_user = get_current_user()
    if not current_user:
        return 'BLA' # TODO better response
    company = Company.query.get(company_id)
    if not company:
        return 'BLAA' # TODO better
    current_user.favorites.remove(company)
    db.session.commit()
    resp = json.dumps({'status': 'ok', 'company_id': company_id})
    print 'remove favorite response = ' + str(resp)
    return resp # TODO better response

@endpoints_bp.route('/send_feedback', methods=['POST', 'GET'])
def send_feedback():
    current_user = get_current_user()
    user_id = None
    if current_user:
        user_id = current_user.id
    data = json.loads(request.data)
    url = data.get('url') 
    text = data.get('text')
    feedback = Feedback(user_id, url, text)
    db.session.add(feedback)
    db.session.commit()
    resp = json.dumps({'status': 'ok'})
    print 'feedback response = ' + str(resp)
    return resp # TODO better response

@endpoints_bp.route('/send_linkedin_message/<friend_id>', methods=['POST', 'GET'])
def send_linkedin_message(friend_id):
    current_user = get_current_user()
    if not current_user:
        return 'Not logged in...' # TODO better error
    data = json.loads(request.data)
    subject =  data.get('subject')
    body = data.get('body')
    body += "\n\n-------------------------\nSent from StartupLinx\nwww.startuplinx.co\nConnecting Students with Startups"
    recipient = User.query.get(friend_id)
    if not recipient:
        return 'ERROR: Recipient not found' # TODO return real error
    message = json.dumps({
        "recipients": {
            "values": [
                {
                  "person": {
                    "_path": "/people/" + str(recipient.linkedin_id)
                   }
                }
            ]
        },
        "subject": subject,
        "body": body
    })
    print current_user.name.encode('utf8') + ' sending linkedin message to ' + recipient.name.encode('utf8') + ':'
    response = post_linkedin_message(message)
    print '...Sent! response data = ' + str(response.data)
     # TODO better error handling
    log_event(current_user.id, 'send_message', {
        'ip': request.remote_addr, 
        'recipient_id': recipient.id,
        'recipient_name': recipient.name,
        'subject': subject,
        'body': body,
        'linkedin_response': response.data
    })
    print 'Logged event'
    resp = json.dumps({'status': 'ok'})
    if 'errorCode' in response.data or 'error' in response.data:
        resp = json.dumps({'status': 'error'})
    print 'send message resp = ' + str(resp)
    return resp

#----------------------------------------------
#              Admin Panel
#----------------------------------------------

@endpoints_bp.route('/admin/create_db')
@admin_only
def admin_create_db():
    print 'Creating database...'
    create_db()
    resp = json.dumps({'status': 'ok'})
    return resp

@endpoints_bp.route('/admin/rescrape_all_companies', defaults={'mode': DEFAULT_RESCRAPE_MODE}, methods=['POST', 'GET'])
@endpoints_bp.route('/admin/rescrape_all_companies/<mode>')
@admin_only
def admin_rescrape_all_companies(mode):
    if mode == SOFT_RESCRAPE_MODE:
        print '   SOFT!!!'
        companies = Company.query.filter(Company.crunchbase_data!=None).all()
    elif mode == FROM_URL_RESCRAPE_MODE:
        print '   FROM URL!!!'
        companies = Company.query.filter(Company.crunchbase_url!=None).all()
    else:
        companies = Company.query.order_by(desc(Company.id)).all()
    print 'Rescraping ' + str(len(companies)) + ' companies:'
    for company in companies:
        print str(company.id) + ': ' + company.name.encode('utf8') # + ' --> ' + len(str(company.crunchbase_data))
    rescrape_companies_from_list(companies, mode)
    resp = json.dumps({'status': 'ok'})
    return resp

@endpoints_bp.route('/admin/rescrape_all_user_images', methods=['POST', 'GET'])
def admin_rescrape_all_user_images():
    users = User.query.filter(User.picture_url!=None, User.local_picture_url==None).all()
    print 'Rescraping ' + str(len(users)) + ' user images:'
    for  user in users:
        print str(user.id) + ': ' + user.name.encode('utf8')
    rescrape_user_images_from_list(users)
    resp = json.dumps({'status': 'ok'})
    return resp

@endpoints_bp.route('/admin/login_as/<user_id>')
@admin_only
def admin_login_as(user_id):
    new_user = User.query.get(user_id)
    if not new_user:
        return 'User does not exist...'
    # TODO abstract away in method -- same in /logout
    session.pop('user_id', None) 
    session.pop('linkedin_id', None) 
    session.pop('admin_mode', None)
    session['user_id'] = new_user.id
    session['linkedin_id'] = new_user.linkedin_id
    return redirect(url_for('feed'))

@endpoints_bp.route('/admin/toggle_admin_mode')
@admin_only
def toggle_admin_mode():
    if session.get('admin_mode'):
        session.pop('admin_mode', None)
    else:
        session['admin_mode'] = True
    return redirect(url_for('admin'))

@endpoints_bp.route('/admin/add_company', methods=['POST', 'GET'])
@admin_only
def admin_add_company():
    data = json.loads(request.data)
    linkedin_id = data.get('linkedin_id')
    name = data.get('name')
    crunchbase_url = data.get('crunchbase_url')
    if not linkedin_id or linkedin_id == "":
        linkedin_id = gen_fake_linkedin_id()
    company = Company(linkedin_id, name)
    company.crunchbase_url = crunchbase_url
    db.session.add(company)
    db.session.commit()
    print ' adding new company for rescraping: ' + name.encode('utf8') + ' --> ' + linkedin_id
    print '              new company id = ' + str(company.id)
    if crunchbase_url and crunchbase_url != "":
        mode = FROM_URL_RESCRAPE_MODE
    else:
        mode = DEFAULT_RESCRAPE_MODE
    rescrape_companies_from_list([company], mode=mode)
    # TODO FUCK FUCK FUCK FUCK HEROKU for not allowing > 1 thread
    # WHAT IN THE FUCKING FUCK.....
    #times_left = 100
    #while not company.is_feed_ready and times_left >= 0:
    #    times_left -= 1 # this is to make sure this doesn't become an infinite for-loop
    #    time.sleep(5)
    #    db.session.commit() # Retarded way to start a new transaction because FUCK sqlalchemy...
    #    print '       ... waiting for scraper callback --> is_feed_ready ' + str(company.is_feed_ready)
    resp = json.dumps({'status': 'ok', 'company_id': company.id})
    return resp 


@endpoints_bp.route('/admin/merge_companies', methods=['POST', 'GET'])
@admin_only
def admin_merge_companies():
    data = json.loads(request.data)
    mother_company_id = data.get('mother_company_id')
    merge_company_ids = data.get('merge_company_ids')
    if not mother_company_id or len(merge_company_ids) == 0:
        return 'Paramters are wrong' # TODO better
    print 'merging companies: ' + str(merge_company_ids)
    print '   with ' + str(mother_company_id)
    merge_companies_query = merge_companies_query_template.format(
        mother_company_id,
        ','.join([str(c_id) for c_id in merge_company_ids])
    )
    print 'Executing: ' + merge_companies_query
    db.engine.execute(merge_companies_query)
    resp = json.dumps({'status': 'ok', 'company_id': mother_company_id})
    return resp

@endpoints_bp.route('/admin/rescrape_select_companies', defaults={'mode': DEFAULT_RESCRAPE_MODE}, methods=['POST', 'GET'])
@endpoints_bp.route('/admin/rescrape_select_companies/<mode>', methods=['POST', 'GET'])
@admin_only
def rescrape_select_companies(mode):
    data = json.loads(request.data)
    company_ids = data.get('company_ids')
    companies = Company.query.filter(Company.id.in_(company_ids)).all()
    print 'Rescraping ' + str(len(companies)) + ' companies:'
    for company in companies:
        print str(company.id) + ': ' + company.name.encode('utf8') # + ' --> ' + len(str(company.crunchbase_data))
    rescrape_companies_from_list(companies, mode)
    resp = json.dumps({'status': 'ok'})
    return resp

