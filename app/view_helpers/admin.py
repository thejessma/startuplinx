import datetime
from datetime import timedelta
import json

from app.models import LoggedEvent
from app.utils import datetime_to_timestamp 

def get_all_messages():
    message_events = LoggedEvent.query.filter_by(method='send_message').order_by(LoggedEvent.created).all()
    messages = [] 
    for m in message_events:
        message = json.loads(m.data_json)
        message['created'] = m.created
        message['sender_id'] = m.user_id
        message['sender_name'] = m.user.name
        if message['sender_id'] == 2266 or message['recipient_id'] == 2266:
            continue
        messages.append(message)
    return messages

def get_daily_events(method=None):
    if method:
        events = LoggedEvent.query.filter_by(method=method).order_by(LoggedEvent.created).all()
    else:
        events = LoggedEvent.query.order_by(LoggedEvent.created).all()
    point_start = events[0].created.date()
    cur_date = point_start
    reg_idx = 0
    data = []
    now = datetime.datetime.now().date()
    while cur_date <= now:
        registered_today = 0
        while reg_idx < len(events) and events[reg_idx].created.date() <= cur_date:
            reg_idx += 1
            registered_today += 1
        data += [registered_today]
        cur_date += timedelta(days=1)
    point_start = datetime_to_timestamp(point_start) * 1000
    return {'pointStart': point_start, 'data': data}
