class DatabaseConstants:
    DATABASE_URI_TEMPLATE = "mysql://root:StartupLyfe2014@startuplinx2.chobzyje65oy.us-east-1.rds.amazonaws.com/%s?charset=utf8&init_command=set%%20character%%20set%%20utf8"
    DATABASE_LOCAL_URI_TEMPLATE = "mysql://root@127.0.0.1:3307/%s?charset=utf8&init_command=set%%20character%%20set%%20utf8"
    DATABASE_NAME = 'startuplinx'
    DATABASE_URI = DATABASE_URI_TEMPLATE % DATABASE_NAME
    DATABASE_LOCAL_URI = DATABASE_LOCAL_URI_TEMPLATE % DATABASE_NAME

# TODO move to environment variables; same for above
class APIConstants:
    FACEBOOK_APP_ID = '566611436798343' # StartupLyfe app
    FACEBOOK_APP_SECRET = 'bc765a46daab2bdd7c0c3b41bc72bc51'
    #FACEBOOK_APP_ID = '253814034636179'  # MomchilApp
    #FACEBOOK_APP_SECRET = '1639a2f3e151fb9c949cceb6e1708c58'
    APP_OAUTH_SECRET_KEY = 'not sure what this is about but the oauth api needs it'
    LINKEDIN_API_KEY = '75cnrrov2108nt'  # StartupLyfe app
    LINKEDIN_SECRET_KEY = 'ZOEzGxbyWYK33kp6'

