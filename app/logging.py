import json
import sys

from models import db, LoggedEvent

def log_event(user_id, method, data):
	try:
		data_json = json.dumps(data)
		event = LoggedEvent(user_id, method, data_json)
		db.session.add(event)
		db.session.commit()
	except:
		print "Unexpected error while logging event:", sys.exc_info()[0]