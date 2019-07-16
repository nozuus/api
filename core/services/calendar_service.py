import core.database.db as base_db


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
    config =  base_db.get_item("config", "calendar")
    if config:
        return config[0]
    return None