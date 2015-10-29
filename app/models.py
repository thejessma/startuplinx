from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import backref, deferred
from sqlalchemy import desc
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy import UniqueConstraint
import json

from constants import DatabaseConstants

db = SQLAlchemy()

def get_datetime():
    return datetime.utcnow()

# copied from http://stackoverflow.com/questions/9116924/how-can-i-achieve-a-self-referencing-many-to-many-relationship-on-the-sqlalchemy
friendship = db.Table(
    'friendships',
    db.Column('friend_a_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('friend_b_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

favorites = db.Table(
    'favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('company_id', db.Integer, db.ForeignKey('companies.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    created = db.Column(db.DateTime, default=get_datetime)
    modified = db.Column(db.DateTime, onupdate=get_datetime)
    linkedin_id = db.Column(db.String(length = 50), unique = True, index = True)
    real_linkedin_id = db.Column(db.String(length = 50), index = True)
    email = db.Column(db.Unicode(100, collation='utf8_general_ci'), unique = True)
    name = db.Column(db.Unicode(100, collation='utf8_general_ci'))
    first_name = db.Column(db.Unicode(100, collation='utf8_general_ci'))
    last_name = db.Column(db.Unicode(100, collation='utf8_general_ci'))
    headline = db.Column(db.Text(collation='utf8_general_ci'))
    linkedin_url = db.Column(db.Text)
    picture_url = db.Column(db.Text)
    local_picture_url = db.Column(db.Text)
    is_registered = db.Column(db.Boolean)
    is_admin = db.Column(db.Boolean)
    last_login = db.Column(db.DateTime)
    last_linkedin_update = db.Column(db.DateTime)
    linkedin_tokens_json = db.Column(db.Text)
    # DON'T USE friends to read. Use all_friends instead
    friends = db.relationship('User', secondary = friendship, primaryjoin=id==friendship.c.friend_a_id, secondaryjoin=id==friendship.c.friend_b_id)
    positions = db.relationship('Position', backref='user')
    favorites = db.relationship('Company', secondary=favorites)
    # TODO apply to remote then remove from here:
    # alter table users add column is_admin tinyint(1) default null after is_registered
    # alter table users add column local_picture_url text after picture_url
    # alter table users add column real_linkedin_id varchar(50) default null after linkedin_id
    # update users set real_linkedin_id = substring(linkedin_url, char_length("https://www.linkedin.com/profile/view?id=") + 1, locate("&authType", linkedin_url) - char_length("https://www.linkedin.com/profile/view?id=") - 1) where real_linkedin_id is null;

    def __init__(self, linkedin_id):
        self.linkedin_id = linkedin_id
        self.is_registered = False
        self.is_admin = False

    def __repr__(self):
        return '<User %r %r>' % (self.linkedin_id, self.name)

    @staticmethod
    def from_linkedin_id(linkedin_id):
        return User.query.filter_by(linkedin_id=linkedin_id).first()

# this relationship is viewonly and selects across the union of all
# friends
# again, taken from http://stackoverflow.com/questions/9116924/how-can-i-achieve-a-self-referencing-many-to-many-relationship-on-the-sqlalchemy
friendship_union = select([
                        friendship.c.friend_a_id,
                        friendship.c.friend_b_id
                        ]).union(
                            select([
                                friendship.c.friend_b_id,
                                friendship.c.friend_a_id]
                            )
                    ).alias()

User.all_friends = db.relationship('User',
                       secondary=friendship_union,
                       primaryjoin=User.id==friendship_union.c.friend_a_id,
                       secondaryjoin=User.id==friendship_union.c.friend_b_id,
                       viewonly=True)

class Position(db.Model):
    __tablename__ = 'positions'
    id = db.Column(db.Integer, primary_key = True)
    created = db.Column(db.DateTime, default=get_datetime)
    modified = db.Column(db.DateTime, onupdate=get_datetime)
    linkedin_id = db.Column(db.String(length = 50), index = True, unique = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index = True) 
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), index = True)
    title = db.Column(db.Text(collation='utf8_general_ci'))
    summary = db.Column(db.Text(collation='utf8_general_ci'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_current = db.Column(db.Boolean)
    last_linkedin_update = db.Column(db.DateTime)

class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key = True)
    created = db.Column(db.DateTime, default=datetime.now)
    modified = db.Column(db.DateTime, onupdate=datetime.now)
    # remote fields
    linkedin_id = db.Column(db.String(length = 50), index = True, unique = True)
    name = db.Column(db.Unicode(100, collation='utf8_general_ci'), index = True)
    logo_url = db.Column(db.Text)
    website_url = db.Column(db.Text)
    email_domains_json = db.Column(db.Text(collation='utf8_general_ci'))
    headquarters_json = db.Column(db.Text(collation='utf8_general_ci'))
    founded_on = db.Column(db.Date)
    founded_on_year = db.Column(db.Integer)
    offices_json = db.Column(db.Text(collation='utf8_general_ci'))
    total_funding = db.Column(db.BigInteger)
    latest_funding_series = db.Column(db.String(length = 50))
    latest_funding_amount = db.Column(db.BigInteger) 
    valuation = db.Column(db.Integer)
    funding_rounds_json = db.Column(db.Text(collation='utf8_general_ci'))
    team_json = db.Column(db.Text(collation='utf8_general_ci'))
    team_size = db.Column(db.Integer)
    employees_min = db.Column(db.Integer)
    employees_max = db.Column(db.Integer)
    summary = db.Column(db.Text(collation='utf8_general_ci'))
    description = db.Column(db.Text(collation='utf8_general_ci'))
    industries_json = db.Column(db.Text(collation='utf8_general_ci'))
    articles_json = db.Column(db.Text(collation='utf8_general_ci'))
    rating_glassdoor = db.Column(db.Float(precision = 32))
    glassdoor_url = db.Column(db.Text)
    crunchbase_url = db.Column(db.Text)
    crunchbase_path = db.Column(db.Text)
    angellist_url = db.Column(db.Text)
    linkedin_url = db.Column(db.Text)
    twitter_url = db.Column(db.Text)
    facebook_url = db.Column(db.Text)
    linkedin_data = db.Column(db.Text(collation='utf8_general_ci'))
    crunchbase_data = db.Column(db.Text(collation='utf8_general_ci'))
    crunchbase_funding_rounds_data = db.Column(db.Text(collation='utf8_general_ci'))
    crunchbase_team_data = db.Column(db.Text(collation='utf8_general_ci'))
    angellist_data = db.Column(db.Text(collation='utf8_general_ci'))
    glassdoor_data = db.Column(db.Text(collation='utf8_general_ci'))
    # local fields
    remote_id = db.Column(db.Integer)
    is_feed_ready = db.Column(db.Boolean)
    last_update = db.Column(db.DateTime)
    positions = db.relationship('Position', backref='company')
    is_startup = db.Column(db.Boolean)
    reported_non_startup = db.Column(db.Integer)
    is_vetted = db.Column(db.Boolean)
    rating = db.Column(db.Float)
    # alter table companies add column is_startup tinyint(1) DEFAULT NULL after last_update; alter table companies add column reported_non_startup int(11) DEFAULT NULL after is_startup; alter table companies add column is_vetted tinyint(1) DEFAULT NULL after reported_non_startup; alter table companies add column rating double DEFAULT NULL after reported_non_startup;
    # alter table companies add column articles_json text;
    # alter table companies add column founded_on DATE after headquarters_json;
    # alter table companies add column founded_on_year INT(11) after founded_on;

    def __init__(self, linkedin_id, name):
        self.linkedin_id = linkedin_id
        self.name = name 
        self.is_feed_ready = False

    def clear_fields(self, fields):
        for field in fields:
            setattr(self, field, None)

    def update(self, field, value):
        if value is not None:
            setattr(self, field, value)
            return True
        return False

    def deserialize_fields(self, fields, company_data):
        updated_count = 0
        for field in fields:
            updated_count += self.update(field, company_data.get(field))
        return updated_count

    def serialize_fields(self, fields):
        company_data = dict()
        for field in fields:
            company_data[field] = getattr(self, field)
        return company_data

    def __repr__(self):
        return '<Company %r %r>' % (self.linkedin_id, self.name)

    @staticmethod
    def from_linkedin_id(linkedin_id):
        return Company.query.filter_by(linkedin_id=str(linkedin_id)).first()


class Education(db.Model):
    __tablename__ = 'educations'
    id = db.Column(db.Integer, primary_key = True)
    created = db.Column(db.DateTime, default=get_datetime)
    modified = db.Column(db.DateTime, onupdate=get_datetime)
    linkedin_id = db.Column(db.String(length = 50), index = True, unique = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index = True) 
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), index = True)
    degree = db.Column(db.Text(collation='utf8_general_ci'))
    field_of_study = db.Column(db.Text(collation='utf8_general_ci'))
    activities = db.Column(db.Text(collation='utf8_general_ci'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    last_linkedin_update = db.Column(db.DateTime)


class School(db.Model):
    __tablename__ = 'schools'
    id = db.Column(db.Integer, primary_key = True)
    created = db.Column(db.DateTime, default=datetime.now)
    modified = db.Column(db.DateTime, onupdate=datetime.now)
    linkedin_id = db.Column(db.String(length = 50), index = True, unique = True)
    identifier = db.Column(db.Unicode(250, collation='utf8_general_ci'), index = True, unique = True)
    name = db.Column(db.Unicode(250, collation='utf8_general_ci'), index = True)
    logo_url = db.Column(db.Text)
    website_url = db.Column(db.Text)
    headquarters_json = db.Column(db.Text(collation='utf8_general_ci'))
    founded_on = db.Column(db.Date)
    founded_on_year = db.Column(db.Integer)
    summary = db.Column(db.Text(collation='utf8_general_ci'))
    description = db.Column(db.Text(collation='utf8_general_ci'))

    def __init__(self, identifier, name):
        self.identifier = identifier 
        self.name = name 

    def __repr__(self):
        return '<School %r %r>' % (self.identifier, self.name)

    @staticmethod
    def from_name(name):
        return School.query.filter(School.name.ilike(name)).first()

    @staticmethod
    def from_identifier(identifier):
        return School.query.filter_by(identifier=identifier).first()

class LoggedEvent(db.Model):
    __tablename__ = 'logged_events'
    id = db.Column(db.Integer, primary_key = True)
    created = db.Column(db.DateTime, default=datetime.now)
    modified = db.Column(db.DateTime, onupdate=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index = True) 
    method = db.Column(db.String(length = 50), index = True)
    data_json = db.Column(db.Text(collation='utf8_general_ci'))
    user = db.relationship('User')

    def __init__(self, user_id, method, data_json):
        self.user_id = user_id
        self.method = method
        self.data_json = data_json

    def __repr__(self):
        return '<LoggedEvent %r %r>' % (self.user_id, self.method)

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key = True)
    created = db.Column(db.DateTime, default=datetime.now)
    modified = db.Column(db.DateTime, onupdate=datetime.now)
    user_id = db.Column(db.Integer, index = True)
    company_id = db.Column(db.Integer, index = True)
    url = db.Column(db.Text(collation='utf8_general_ci'))
    text = db.Column(db.Text(collation='utf8_general_ci'))
    data_json = db.Column(db.Text(collation='utf8_general_ci'))

    def __init__(self, user_id, url, text):
        self.user_id = user_id
        self.url = url
        self.text = text

    def __repr__(self):
        return '<Feedback %r %r>' % (self.user_id, self.text)

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key = True)
    created = db.Column(db.DateTime, default=datetime.now)
    modified = db.Column(db.DateTime, onupdate=datetime.now)
    user_id = db.Column(db.Integer, index = True)
    title = db.Column(db.Unicode(1000, collation='utf8_general_ci'))
    subtitle = db.Column(db.Text(collation='utf8_general_ci'))
    url = db.Column(db.Text(collation='utf8_general_ci'))
    author_name = db.Column(db.Unicode(100, collation='utf8_general_ci'))
    image_url = db.Column(db.Text)
    content = db.Column(db.Text(collation='utf8_general_ci'))
    mins_to_read = db.Column(db.Integer)
    order_id = db.Column(db.Integer)
    is_visible = db.Column(db.Boolean)

    def __init__(self, user_id):
        self.user_id = user_id
        self.is_visible = False

    def __repr__(self):
        return '<Article %r %r>' % (self.title, self.author_name)

class Campaign(db.Model):
    __tablename__ = 'campaigns'
    id = db.Column(db.Integer, primary_key = True)
    created = db.Column(db.DateTime, default=get_datetime)
    modified = db.Column(db.DateTime, onupdate=get_datetime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index = True) 
    name = db.Column(db.Unicode(100, collation='utf8_general_ci'))
    sender_name = db.Column(db.Unicode(100, collation='utf8_general_ci'))
    sender_email = db.Column(db.Unicode(100, collation='utf8_general_ci'))
    subject_template = db.Column(db.Text(collation='utf8_general_ci'))
    body_template = db.Column(db.Text(collation='utf8_general_ci'))
    is_ready = db.Column(db.Boolean)

    def __init__(self, user_id):
        self.user_id = user_id
        self.is_ready = False

class Recipient(db.Model):
    __tablename__ = 'recipients'
    id = db.Column(db.Integer, primary_key = True)
    created = db.Column(db.DateTime, default=get_datetime)
    modified = db.Column(db.DateTime, onupdate=get_datetime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index = True) 
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), index = True)
    is_sent = db.Column(db.Boolean)
    sent_via_linkedin = db.Column(db.DateTime)
    sent_via_email = db.Column(db.DateTime)
    emails_json = db.Column(db.Text(collation='utf8_general_ci'))
    fields_json = db.Column(db.Text(collation='utf8_general_ci'))
    subject = db.Column(db.Text(collation='utf8_general_ci'))
    body = db.Column(db.Text(collation='utf8_general_ci'))

# call this somewhere in application.py/home, run and open home page
# then check if db is created and then remove it
# TODO (mom) I know, it's super ghetto, but that's the easiest way for now
def create_db():
    db.create_all()
