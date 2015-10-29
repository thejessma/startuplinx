from flask import Flask, render_template
import _mysql
import os

app = Flask(__name__)

conn = _mysql.connect(host='127.0.0.1', db='startuplyfe', user='root')

def select_single_row(query):
    conn.query(query)
    result = conn.use_result()
    row = result.fetch_row(1)
    if row:
        return row[0]
    else:
        return None


class Person:

    def load(self, facebook_id):
        data = select_single_row('SELECT * FROM people WHERE facebook_id=\'{0}\' LIMIT 1'.format(facebook_id))
        if data:
            self.id = data['id']
            self.created = data['created']

    def __init__(self, facebook_id, is_me=False):
        self.load(facebook_id)

    def 



@app.route('/')
def hello_world():

    Person p = Person('1454031404', is_me=True)

    #return render_template('facebook.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True) # TODO (mom) remove debug before release
