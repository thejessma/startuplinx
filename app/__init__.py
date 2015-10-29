# -*- coding: utf-8 -*-

from flask import Flask

# api's
from api_helpers.facebook import facebook_bp
from api_helpers.linkedin import linkedin_bp
from endpoints import endpoints_bp

# database
from models import db

# constants
from constants import APIConstants, DatabaseConstants

app = Flask(__name__)

# app properties required for API's
app.secret_key = APIConstants.APP_OAUTH_SECRET_KEY

# make jinja do cool stuff
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

# "include" API's
app.register_blueprint(facebook_bp)
app.register_blueprint(linkedin_bp)

# "include" our own api
app.register_blueprint(endpoints_bp)

# configure database
app.config['SQLALCHEMY_DATABASE_URI'] = DatabaseConstants.DATABASE_URI
db.init_app(app)

from app import views
