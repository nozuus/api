import core.database.db as base_db
import core.database.users_db as users_db
import requests
from icalendar import Calendar, Event
from datetime import datetime
import hashlib
import os
import json
from dateutil.parser import parse


def set_configuration(calendar_type, api_key, url):
    item = {
        "pk": "config",
        "sk": "calendar",
        "type": calendar_type,
        "api_key": api_key,
        "calendar_url": url
    }
    return base_db.put_item_no_check(item)


def get_configuraiton():
    return base_db.get_item("config", "calendar")


def generate_cal_link_for_user(user_email):
    user = users_db.get_user_by_email(user_email)
    if user is None:
        raise Exception("Invalid user email")
    token = hashlib.sha512(user_email.encode("utf-8")).hexdigest()

    token = token[0:30]

    stage = os.environ.get("stage")
    base_url = "http://localhost:5000/"
    if stage is not None:
        base_url = "https://%s-api.theotterpond.com/" % stage

    base_db.put_item_no_check({"pk": user_email, "sk": "calendar_%s" % token})

    return base_url + "calendar/" + token + "/calendar"


def get_ics(user_token):
    token_record = base_db.get_items_by_type("calendar_%s" % user_token)
    if len(token_record) == 0:
        raise Exception("Invalid user token")
    else:
        print("User refreshing ICS: " + token_record[0]["pk"])
    config = get_configuraiton()
    url = "https://www.googleapis.com/calendar/v3/calendars/%s/events?key=%s" % (config["calendar_url"], config["api_key"])
    events = requests.get(url).json()
    print (json.dumps(events))
    cal = Calendar()
    cal["summary"] = "Georgia Tech Delta Chi Calendar"
    cal["name"] = "GT Delta Chi"
    cal.add('prodid', '-//GT Delta Chi//mxm.dk//')
    cal.add('version', '1.0')

    for event_json in events["items"]:
        try:
            if event_json["status"] == "cancelled":
                continue
            event = Event()
            event.add("summary", event_json["summary"])
            event.add("uid", event_json["iCalUID"])
            if "date" in event_json["start"]:
                start = parse(event_json["start"]["date"])
                end = parse(event_json["end"]["date"])
                event.add("dtstart", start)
                event.add("dtend", end)
            else:
                start = parse(event_json["start"]["dateTime"])
                end = parse(event_json["end"]["dateTime"])
                event.add("dtstart", start)
                event.add("dtend", end)
            cal.add_component(event)
        except Exception as e:
            print (e)
            print (event_json)

    result = cal.to_ical()
    return result