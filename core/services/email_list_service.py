import core.database.email_list_db as email_list_db
import core.database.users_db as users_db
import core.database.email_list_db as email_db


def add_to_list(user_id, prefix, domain):
    user = users_db.get_user_by_id(user_id)
    primary_email = user["primary_email_address"]
    list_id = email_db.get_email_list(prefix, domain)["list_id"]
    subscription = {
        "user_id": user_id,
        "list_id": list_id,
        "user_primary_email_address": primary_email
    }
    email_list_db.add_to_list(subscription)