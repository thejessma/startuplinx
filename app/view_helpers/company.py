import json
import string
import urllib
import urllib2
from flask import url_for
import random

REMOTE_SCRAPER_URL = 'http://54.172.148.221:5000/scrape_companies'

DEFAULT_RESCRAPE_MODE = 'search'
SOFT_RESCRAPE_MODE = 'soft'
FROM_URL_RESCRAPE_MODE = 'from_url'

LINKEDIN_COMPANY_URL_PREFIX = 'http://www.linkedin.com/company/'

# same as remote
# note that we do not update the company name b/c we might have 
# fetched the wrong company
SUPPORTED_FIELDS = [
        'name', # TODO TODO remove after rescrape
        'crunchbase_url',
        'crunchbase_path',
        'logo_url',
        'description',
        'summary',
        'email_domains_json',
        'website_url',
        'headquarters_json',
        'founded_on',
        'founded_on_year',
        'offices_json',
        'total_funding',
        'latest_funding_series',
        'latest_funding_amount',
        'valuation',
        'funding_rounds_json',
        'team_json',
        'team_size',
        'employees_min',
        'employees_max',
        'industries_json',
        'articles_json',
        'linkedin_url',
        'twitter_url',
        'facebook_url',
        'crunchbase_data',
        'linkedin_data'
]

ADMIN_ADVANCED_FIELDS = [
        'linkedin_id',
        'remote_id',
        'is_feed_ready',
        'is_startup',
        'reported_non_startup',
        'is_vetted',
        'rating'
] + SUPPORTED_FIELDS

ADMIN_BASIC_FIELDS = [
        'name',
        'is_startup',
        'is_vetted',
        'rating',
        'logo_url',
        'website_url',
        'team_size',
        'employees_min',
        'employees_max',
        'total_funding',
        'latest_funding_series',
        'latest_funding_amount',
        'summary',
        'description'
]

def scrape_companies(new_companies_data):
    print ' sending ' + str(len(new_companies_data)) + ' new companies for SCRAPING...'
    data = urllib.urlencode({'data': json.dumps(new_companies_data)})
    req = urllib2.Request(REMOTE_SCRAPER_URL, data)
    resp = urllib2.urlopen(req)
    resp_html = resp.read()
    print ' response was ' + str(resp_html)

feed_company_fields = """
    c.id as company_id, c.name as company_name, c.logo_url, c.headquarters_json, c.founded_on_year, c.summary,
    c.employees_min, c.employees_max, c.team_size, c.latest_funding_series, c.total_funding, c.funding_rounds_json, c.website_url, c.is_startup,
    (exists (select company_id from favorites where user_id = {0} and company_id = c.id)) as is_favorited
"""

feed_friend_fields = """
    f.id as friend_id, f.name, f.picture_url, f.local_picture_url
"""

profile_company_extra_fields = """
    c.description, c.team_json, c.articles_json, c.linkedin_id, c.linkedin_url
"""

profile_friend_extra_fields = """
    p.title as position, f.first_name,
    (f.id in (
             select friend_a_id id 
             from friendships 
             where friend_b_id = {0} 
         union 
             select friend_b_id id 
             from friendships
             where friend_a_id = {0}
        )
    ) as is_friend,
    (select s.name
     from schools s
     where exists (
             select 1 from educations where user_id = f.id and school_id = s.id
         )
         and exists (
             select 1 from educations where user_id = {0} and school_id = s.id
         )
     limit 1
    ) as common_school
"""

friends_and_classmates_subquery = """
        select friend_a_id id 
        from friendships 
        where friend_b_id = {0} 
    union 
        select friend_b_id id 
        from friendships
        where friend_a_id = {0}
    union
        select e.user_id id
        from educations e 
        join schools s
            on e.school_id = s.id
        where s.id in (
            select sch.id
            from schools sch
            join educations ed
                on sch.id = ed.school_id
            where ed.user_id = {0}
        )
"""

feed_companies_query_template = """
    select %s 
    from positions p
    join companies c 
        on p.company_id = c.id 
    join users f
        on p.user_id = f.id
    where c.logo_url is not null 
        and c.is_feed_ready
        and f.id in (%s)
    group by c.id
""" % (feed_company_fields, friends_and_classmates_subquery)

feed_friends_query_template = """
    select c.id as company_id, %s
    from positions p
    join companies c 
        on p.company_id = c.id 
    join users f
        on p.user_id = f.id
    where c.logo_url is not null 
        and c.is_feed_ready
        and f.id in (%s)
    group by c.id, f.id
""" % (feed_friend_fields, friends_and_classmates_subquery)

feed_vetted_companies_query_template = """
    select %s 
    from companies c 
    where c.logo_url is not null 
        and c.is_feed_ready
        and c.is_vetted
        and c.is_startup
        and c.id not in ({1})
""" % (feed_company_fields)

feed_companies_pending_query_template = """
    select count(distinct c.id) as cnt
    from positions p
    join companies c 
        on p.company_id = c.id 
    join users f
        on p.user_id = f.id
    where not c.is_feed_ready 
        and f.id in (%s)
""" % (friends_and_classmates_subquery)

profile_company_query_template = """
    select %s, %s from companies c where c.id = {0}
""" % (feed_company_fields, profile_company_extra_fields)

profile_friends_query_template = """
    select c.id as company_id, %s, %s
    from positions p
    join companies c 
        on p.company_id = c.id 
    join users f
        on p.user_id = f.id
    where c.id = {1}
        and f.id in (%s)
    group by f.id
""" % (feed_friend_fields, profile_friend_extra_fields, friends_and_classmates_subquery)

profile_all_employees_query_template = """
    select c.id as company_id, %s, %s
    from positions p
    join companies c 
        on p.company_id = c.id 
    join users f
        on p.user_id = f.id
    where c.id = {0}
    group by f.id
""" % (feed_friend_fields, profile_friend_extra_fields)

kuenne_ceos_and_founders_query_template = """
    select u.id as user_id, c.id as company_id, first_name, last_name, u.email as email, headline, p.title as title, c.name as company_name, c.website_url as website_url, c.email_domains_json as email_domains_json, c.linkedin_id as company_linkedin_id from users u join friendships f on u.id = friend_b_id join positions p on p.user_id=u.id join companies c on c.id=p.company_id where friend_a_id = {0} and (headline like '%%CEO%%' or headline like '%%founder%%') and (p.title not like '%%to the CEO%%') 
"""

#TODO DANGER ZONE -- might wanna replace this brave delete with is_deleted = True
merge_companies_query_template = """
update positions set company_id = {0} where company_id in ({1});
update feedback set company_id = {0} where company_id in ({1});
delete from companies where id in ({1});
"""

FILTER_POINTS_THRESHOLD = 3
# TODO move to utils
def random_string(size=16, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

# THIS IS important!!! I use the assumption that fake linkedin_ids start with FAKE all over the place,
# including in celery
def gen_fake_linkedin_id():
    return 'FAKE_' + random_string(32)

def is_fake_linkedin_id(linkedin_id):
    if not linkedin_id:
        return True
    if linkedin_id.startswith('FAKE'):
        return True
    return False

def prepare_companies_for_feed(companies, filter=None):
    # randomize & sort
    companies = [(c['startup_points'], random.randint(1, 100), id, c) for id, c in companies.iteritems()]
    if filter == 'startups':
        companies = [c for c in companies if c[0] >= FILTER_POINTS_THRESHOLD]
    elif filter == 'nonstartups':
        companies = [c for c in companies if c[0] < FILTER_POINTS_THRESHOLD]
    companies.sort()
    companies.reverse()
    # split into 4 vertical columns
    companies_vertical = []
    for vertical_id in range(4):
        companies_vertical.append(companies[vertical_id:len(companies):4])
    return companies_vertical

# TODO move to helper function files...along with all other crap
def compact_moneyz(moneyz):
    if moneyz >= 1000000000:
        return '$' + str(int(round(moneyz/1000000000))) + 'B'
    if moneyz >= 1000000:
        return '$' + str(int(round(moneyz/1000000))) + 'M'
    if moneyz >= 1000:
        return '$' + str(int(round(moneyz/1000))) + 'K'
    return '$' + moneyz

def get_company_info_from_query_result(result, include_profile_info=False):
    startup_points = 0
    if result['is_startup']:
        startup_points += 1000 # if we say it's a startup, it's a startup
    elif result['is_startup'] == False:
        startup_points -= 1000 # if we say it's not a startup, it's not a startup
    # calc employees
    employees = ''
    employees_min = 0 # note that 0 = unknown/undefined for filtering
    employees_max = 0 # same
    if result['employees_min'] and result['employees_max']:
        employees = str(result['employees_min']) + '-' + str(result['employees_max'])
        employees_min = result['employees_min']
        employees_max = result['employees_max']
        if int(result['employees_max']) > 10000:
            startup_points -= 100 # not a startup
        elif int(result['employees_max']) > 2000:
            startup_points += 0
        else:
            startup_points += 2
    elif result['team_size']:
        employees = str(result['team_size'])
        employees_min = employees
        employees_max = employees
        if int(result['team_size']) > 2500:
            startup_points -= 100
        elif int(result['team_size'] > 1000):
            startup_points += 0 # not a startup
        else:
            startup_points += 2
    if employees:
        startup_points += 1
    # calc investors
    investors = []
    if result['funding_rounds_json']:
        funding_rounds = json.loads(result['funding_rounds_json'])
        for funding_round in funding_rounds:
            announced_on = funding_round['announced_on']
            for investment in funding_round['investments']:
                investors.append((announced_on, investment['investor']))
        investors.sort()
        investors.reverse()
    if len(investors) > 0:
        startup_points += 1
    # calc HQ
    headquarters = ''
    if result['headquarters_json']:
        headquarters = json.loads(result['headquarters_json'])
        if headquarters['city']:
            headquarters = headquarters['city']
        elif headquarters['country']:
            headquarters = headquarters['country']
    if headquarters:
        startup_points += 1
    # calc total funding
    total_funding = compact_moneyz(int(result['total_funding'])) if result['total_funding'] else '--'
    if total_funding != '--':
        startup_points += 1
    total_funding_numeric = int(result['total_funding']) if result['total_funding'] else 0 # note that 0 = undefined/unknown funding for filtering
    # calc latest series
    latest_funding_series = str(result['latest_funding_series']) if result['latest_funding_series'] else '--'
    if latest_funding_series != '--':
        startup_points += 1
        latest_funding_series_value = ord(latest_funding_series[0]) - ord('A') + 1 # A -> 1, B -> 2, etc
    else:
        latest_funding_series_value = 0 # note for filtering, 0 == undefined / unknown (same as seed)
    # serialize for frontend
    company = {
        'id': result['company_id'],
        'name': result['company_name'],
        'website_url': result['website_url'],
        'logo_url': result['logo_url'],
        'headquarters_json': result['headquarters_json'].lower() if result['headquarters_json'] else "", # for filtering, "" == undefined / unknown
        'founded_on_year': result['founded_on_year'] if result['founded_on_year'] else 0, # note for filtering, 0 == undefined / unknown
        'summary': result['summary'] if result['summary'] else "",
        'employees': employees,
        'employees_min': employees_min,
        'employees_max': employees_max,
        'latest_funding_series': latest_funding_series,
        'latest_funding_series_value': latest_funding_series_value,
        'total_funding': total_funding,
        'total_funding_numeric': total_funding_numeric,
        'investors': [x[1] for x in investors[:3]],
        'headquarters': headquarters,
        'startup_points': startup_points,
        'is_favorited': result['is_favorited']
    }

    # this is extended company info for the profile page
    if include_profile_info:
        company['description'] = result['description']
        if company['description']:
            company['description'] = company['description'].replace('\n', '<br>')
        # calc funding rounds
        company['funding_rounds'] = []
        if result['funding_rounds_json']:
            funding_rounds = json.loads(result['funding_rounds_json'])
            rounds_info = []
            for funding_round in funding_rounds:
                announced_on = funding_round.get('announced_on')
                round_info = {
                    'series': str(funding_round.get('series').upper()) if funding_round.get('series') else '--',
                    'amount': compact_moneyz(int(funding_round.get('money_raised_usd'))) if funding_round.get('money_raised_usd') else '--',
                    'year': str(funding_round.get('announced_on_year')) if funding_round.get('announced_on_year') else '--',
                    'investors': []
                }
                for investment in funding_round['investments']:
                    round_info['investors'].append(investment['investor'])
                rounds_info.append((announced_on, round_info))
            rounds_info.sort()
            rounds_info.reverse()
            company['funding_rounds'] = [x[1] for x in rounds_info]
        # calc team
        company['team'] = []
        if result['team_json']:
            team = json.loads(result['team_json'])
            for member in team:
                if member.get('first_name') and member.get('last_name') and member.get('photo_url'):
                    bio = member.get('bio')
                    truncated_bio = bio
                    if bio and len(bio) > 290:
                        cutoff = bio[:290].rfind(' ')
                        if cutoff > -1:
                            truncated_bio = bio[:cutoff] + '...'
                    member_info = {
                        'name': member['first_name'] + ' ' + member['last_name'],
                        'photo_url': member['photo_url'],
                        'title': member.get('title') if 'title' in member else '',
                        'bio': bio if bio else '',
                        'truncated_bio': truncated_bio if truncated_bio else '',
                        'experience': member.get('experience') if 'experience' in member else []
                    }
                    company['team'].append(member_info)
        # calc articles 
        company['articles'] = []
        if result['articles_json']:
            articles = json.loads(result['articles_json'])
            for article in articles:
                company['articles'].append(article)
        # calc linkedin url
        company['linkedin_url'] = result['linkedin_url']
        if not company['linkedin_url'] and not is_fake_linkedin_id(result['linkedin_id']):
            company['linkedin_url'] = LINKEDIN_COMPANY_URL_PREFIX + result['linkedin_id']
    return company

def get_friend_info_from_query_result(result, include_profile_info=False):
    # only show friends with photos TODO WTF linkedin...
    if not result['picture_url'] and not result['local_picture_url']:
        return None
    friend = {
        'id': result['friend_id'],
        'name': result['name'],
        'picture_url': result['local_picture_url'] if result['local_picture_url'] else result['picture_url']
    }
    if include_profile_info:
        friend['position'] = result['position']
        friend['first_name'] = result['first_name']
        friend['is_friend'] = result['is_friend']
        friend['common_school'] = result['common_school']
    return friend

def get_companies_and_friends_feed_info_from_query_results(companies_results, friends_results):
    companies = dict()
    # get company info
    for result in companies_results:
        company = get_company_info_from_query_result(result, include_profile_info=False)
        if not company:
            continue
        id = result['company_id']
        companies[id] = company
        if 'friends' not in companies[id]:
            companies[id]['friends'] = []
    # get friends info
    for result in friends_results:
        friend = get_friend_info_from_query_result(result, include_profile_info=False)
        id = result['company_id']
        if friend:
            companies[id]['friends'].append(friend)
    return companies

def get_company_and_friends_profile_info_from_query_results(company_result, friends_results):
    # get company info
    company = get_company_info_from_query_result(company_result, include_profile_info=True)
    if not company:
        return None
    company['friends'] = []
    # get friends info
    for result in friends_results:
        friend = get_friend_info_from_query_result(result, include_profile_info=True)
        if friend:
            company['friends'].append(friend)
    return company

def rescrape_companies_from_list(companies, mode=DEFAULT_RESCRAPE_MODE):
    new_companies_data = []
    for company in companies:
        new_company_data = {
            'name': company.name,
            'linkedin_id': company.linkedin_id,
            'mode': mode,
            'callback_url': url_for('endpoints_bp.scraper_callback', company_id=company.id, _external=True)}
        if mode == SOFT_RESCRAPE_MODE:
            new_company_data['remote_id'] = company.remote_id
        elif mode == FROM_URL_RESCRAPE_MODE:
            new_company_data['crunchbase_url'] = company.crunchbase_url
        new_companies_data.append(new_company_data)
    scrape_companies(new_companies_data)

