from flask_oauthlib.client import OAuth
import json
from flask import url_for, Blueprint, session, redirect, request, render_template
import flask_oauthlib

from app.constants import APIConstants
from app.models import User

# NOTE: locally, always open as localhost:5000
# MAKE SURE that caching is disabled when testing...
# or test with /login

linkedin_bp = Blueprint('linkedin_bp', __name__)
oauth = OAuth(linkedin_bp)

USER_PROFILE_FIELDS = "(id,first-name,last-name,email-address,headline,site-standard-profile-request,picture_url,positions,educations)"

def new_linkedin_oauth_object(API_KEY, API_SECRET, do_register=True):
    linkedin = oauth.remote_app(
        'linkedin',
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        request_token_params={
            'scope': 'r_fullprofile,r_network,w_messages,r_emailaddress',
            'state': 'RandomString',
        },
        base_url='https://api.linkedin.com/v1/',
        request_token_url=None,
        access_token_method='POST',
        access_token_url='https://www.linkedin.com/uas/oauth2/accessToken',
        authorize_url='https://www.linkedin.com/uas/oauth2/authorization',
        register=do_register
    )
    return linkedin

print 'FUCKING haNDshaKE'
linkedin = new_linkedin_oauth_object(
        APIConstants.LINKEDIN_API_KEY,
        APIConstants.LINKEDIN_SECRET_KEY)
print 'done with handshake...'
default_linkdin = linkedin

@linkedin.tokengetter
def get_linkedin_oauth_token():
    return session.get('linkedin_token')

def get_linkedin_id():
    return session.get('linkedin_id')

def change_linkedin_query(uri, headers, body):
    auth = headers.pop('Authorization')
    headers['x-li-format'] = 'json'
    if auth:
        auth = auth.replace('Bearer', '').strip()
        if '?' in uri:
            uri += '&oauth2_access_token=' + auth
        else:
            uri += '?oauth2_access_token=' + auth
    return uri, headers, body

linkedin.pre_request = change_linkedin_query

# User Scraper helpers

def get_current_linkedin_user():
    user = User.from_linkedin_id(get_linkedin_id())
    return user

def fetch_current_linkedin_id():
    me = linkedin.get('people/~:(id)').data
    return me['id']

def fetch_current_linkedin_user_data():
    return linkedin.get('people/~:' + USER_PROFILE_FIELDS).data

def fetch_current_linkedin_user_connections_data():
    return linkedin.get('people/~/connections:' + USER_PROFILE_FIELDS).data

def fetch_linkedin_company_data(company_id):
    return linkedin.get('companies/' + company_id + ':(id,name,universal-name,email-domains,company-type,ticker,website-url,industries,status,logo-url,square-logo-url,blog-rss-url,twitter-id,employee-count-range,specialties,locations,description,stock-exchange,founded-year,end-year,num-followers)').data

def fetch_linkedin_school_people(school_name):
    return linkedin.get('people-search?school-name=' + school_name).data

# Login helpers

def linkedin_login():
    return linkedin.authorize(callback=url_for('linkedin_bp.linkedin_authorized', _external=True))

def linkedin_logout():
    session.pop('linkedin_token', None)
    session.pop('linkedin_id', None)

@linkedin_bp.route('/linkedin_authorized')
def linkedin_authorized():
    resp = linkedin.authorized_response()
    print 'Resp = ' + str(resp)
    print type(resp)
    if resp is None or isinstance(resp, flask_oauthlib.client.OAuthException):
        message = 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
        return render_template('error', message=message)
    session['linkedin_token'] = (resp['access_token'], '')
    session['linkedin_id'] = fetch_current_linkedin_id()
    return redirect(url_for('login_callback'))

# UX helpers

def post_linkedin_message(message):
    return linkedin.post('people/~/mailbox', data=message, content_type='application/json')

# Debuggin helpers TODO remove in prod

@linkedin_bp.route('/_linkedin_me')
def linkedin_me():
    me = fetch_current_linkedin_user_data()
    return json.dumps(me)

@linkedin_bp.route('/_linkedin_user/<linkedin_id>')
def linkedin_user(linkedin_id):
    me = linkedin.get('people/id=' + str(linkedin_id) + ':' + USER_PROFILE_FIELDS).data
    return json.dumps(me)

@linkedin_bp.route('/_linkedin_connections')
def linkedin_connections():
    me = fetch_current_linkedin_user_connections_data()
    return json.dumps(me)

@linkedin_bp.route('/_linkedin_company/<company_id>')
def linkedin_company(company_id):
    data = fetch_linkedin_company_data(company_id)
    return json.dumps(data)

@linkedin_bp.route('/_linkedin_school_people/<school_name>')
def linkedin_school_people(school_name):
    data = fetch_linkedin_school_people(school_name)
    return json.dumps(data)

# Kuenne multi-account shits

LINKEDIN_API_AND_SECRET_KEYS = [
    ('75cnrrov2108nt', 'ZOEzGxbyWYK33kp6'),
    ('75j8afjklkn1sg', 'ZIrbkkOEcP09GilL'),
    ('75mc0klssy9xa2', '9cH2HsWcjAVeoUVX'),
    ('75bjywlaawl50p', '0yxmOPsbbP9985N9'),
    ('75xzqjitlonw8j', 'BSm2D3RVe4DkCsQN'),
    ('751yv91hvwziyo', '5bsbxP5YCpLQcZWf'),
    ('75jpspf66ik6u8', 'QdfKBSv4U4TokabW'),
    ('75jrfiid84fhzs', 'UQgU0cZFFg6mTMyn'),
    ('755vf70f21zvd4', 'Ea5iGc6dsHKSNARH'),
    ('752138hwyfc3p7', 'IGtStQ5VIliQc086')
]

def kuenne_set_current_linkedin_app(app_idx):
    global linkedin
    linkedin = new_linkedin_oauth_object(
        LINKEDIN_API_AND_SECRET_KEYS[app_idx][0],
        LINKEDIN_API_AND_SECRET_KEYS[app_idx][1],
        do_register=False
    )

def kuenne_reset_linkedin_app():
    global linkedin
    linkedin = default_linkdin

def kuenne_linkedin_multilogin(app_idx):
    app_idx = int(app_idx)
    print 'Kuenne linkedin MULTIlogin with app_idx = ' + str(app_idx)
    session['kuenne_linkedin_app_idx'] = app_idx
    if LINKEDIN_API_AND_SECRET_KEYS[app_idx][0] == APIConstants.LINKEDIN_API_KEY and LINKEDIN_API_AND_SECRET_KEYS[app_idx][1] == APIConstants.LINKEDIN_SECRET_KEY:
        # if it's the default app, shortcut the actual login step
        token = get_linkedin_oauth_token()
        session['kuenne_linkedin_token'] = token 
        print 'shortcut for app_idx = ' + str(app_idx) + ', access token = ' + str(token)
        return redirect(url_for('kuenne_login_callback'))
    else:
        # otherwise, actually login
        kuenne_set_current_linkedin_app(app_idx)
        return linkedin.authorize(callback=url_for('linkedin_bp.kuenne_linkedin_authorized', _external=True))

@linkedin_bp.route('/kuenne_linkedin_authorized')
def kuenne_linkedin_authorized():
    resp = linkedin.authorized_response()
    if resp is None:
        message = 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
        return render_template('error', message=message)
    # DO NOT SET THE LINKEDIN ID!!! we will create a new user and fuck up the db...
    print 'response = ' + str(resp)
    token = (resp['access_token'], '')
    session['kuenne_linkedin_token'] = token
    app_idx = session.get('kuenne_linkedin_app_idx')
    print 'Kuenne linkedin AUTHORITZED with app_idx = ' + str(app_idx)
    print '        access token = ' + str(token)
    kuenne_reset_linkedin_app()
    return redirect(url_for('kuenne_login_callback'))
