from flask import Flask, redirect, url_for, session, request, Blueprint
from flask_oauthlib.client import OAuth, OAuthException
import json

from app.constants import APIConstants

# NOTE: locally, always open as localhost:5000
# otherwise facebook complains

facebook_bp = Blueprint('facebook_bp', __name__)
oauth = OAuth(facebook_bp)

facebook = oauth.remote_app(
    'facebook',
    consumer_key=APIConstants.FACEBOOK_APP_ID,
    consumer_secret=APIConstants.FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email,user_friends'},
    base_url='https://graph.facebook.com',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth'
)

@facebook_bp.route("/facebook_login", methods = ['GET'])
def facebook_login():
    callback = url_for(
        'facebook_bp.facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True
    )
    return facebook.authorize(callback=callback)

@facebook_bp.route('/facebook_login/authorized')
def facebook_authorized():
    resp = facebook.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, OAuthException):
        return 'Access denied: %s' % resp.message
    session['facebook_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    print me.data
    # FUCK FUCK FUCK FUCK FUCK FUCK FUCK FUCK FUCK FUCK... facebook doesn't support this... FUCK
    # http://stackoverflow.com/questions/23417356/facebook-graph-api-v2-0-me-friends-returns-empty-or-only-friends-who-also-use-m
    # https://developers.facebook.com/docs/apps/faq
    # https://developers.facebook.com/bugs/1502515636638396/ 
    friends = facebook.get('/me/friends?fields=id,name,work')
    print friends.data
    return 'Logged in as id=%s name=%s redirect=%s' % \
        (me.data['id'], me.data['name'], request.args.get('next'))

@facebook_bp.route("/facebook_logout", methods = ['GET'])
def facebook_logout():
    session.pop('facebook_token', None)
    return 'Logged out'


@facebook_bp.route('/facebook_test')
def facebook_test():
    friends = facebook.get('/me/taggable_friends?fields=id,name')
    #print friends.data
    return json.dumps(friends.data)

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')
