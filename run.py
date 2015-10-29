#!venv/bin/python
import os
from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', threaded=True, port=port, debug=True) # TODO (mom) remove debug before release
