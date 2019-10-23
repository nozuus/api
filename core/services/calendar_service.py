import core.database.db as base_db
import core.database.users_db as users_db
import requests
from icalendar import Calendar, Event, Timezone
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

    return base_url + "calendar/" + token + "/calendar.ics"


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
    cal.add('prodid', '-//The Otter Pond//GT Delta Chi//EN')
    cal.add('version', '2.0')

    tz = Timezone()
    tz.add("tzid", "America/New_York")

    cal.add_component(tz)

    for event_json in events["items"]:
        try:
            if event_json["status"] == "cancelled":
                continue
            event = Event()
            event.add("summary", event_json["summary"])
            event.add("uid", event_json["iCalUID"])
            start = None
            if "date" in event_json["start"]:
                start = parse(event_json["start"]["date"])
                end = parse(event_json["end"]["date"])
                event.add("dtstart", start.date())
                event.add("dtend", end.date())
            else:
                start = parse(event_json["start"]["dateTime"])
                end = parse(event_json["end"]["dateTime"])
                event.add("dtstart", start)
                event.add("dtend", end)
            if "recurrence" in event_json:
                rule_str = event_json["recurrence"][0][6:]
                rules = rule_str.split(";")
                rule_obj = {}
                for rule in rules:
                    split = rule.split("=")
                    if split[0] == "UNTIL":
                        rule_obj["UNTIL"] = parse(split[1])
                    else:
                        rule_obj[split[0]] = split[1]
                event.add("rrule", rule_obj)
            cal.add_component(event)
        except Exception as e:
            print (e)
            print (event_json)

    result = cal.to_ical()
    return result