import os
import urllib2
from flask import Flask, redirect, url_for, session

CRUNCHBASE_USER_KEY = '777bdddfa10b5b8ef896e4be26ebd75c'

class CrunchBaseAPI:
    url_template = 'http://api.crunchbase.com/v/2/{0}?user_key={1}&page={2}&order={3}'
    orders = [
        'created_at+DESC',
        'created_at+ASC',
        'updated_at+DESC',
        'updated_at+ASC'
    ]

    def __init__(self, user_key):
        self.user_key = user_key

    def get(self, operation, page=1, order='created_at+ASC'):
        url = CrunchBaseAPI.url_template.format(operation, self.user_key, page, order)
        return urllib2.urlopen(url).read()


app = Flask(__name__)
app.debug = True
app.secret_key = 'development'

crunchbase = CrunchBaseAPI(CRUNCHBASE_USER_KEY)

@app.route('/')
def index():
    me = crunchbase.get('products')
    return str(me)


if __name__ == '__main__':
    app.run()
