from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('facebook.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True) # TODO (mom) remove debug before release
