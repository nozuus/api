import core.database.users_db as users_db
import core.database.email_list_db as email_list_db
import uuid


def create_user(user):
    user["sk"] = "user"
    user["pk"] = user.pop("user_email")
    if users_db.create_user(user):
        return True
    else:
        raise Exception("Failed to create user")


def update_user(user_email, new_values):
    user = users_db.get_user_by_email(user_email)
    for key in new_values:
        ##TODO: figure out how to handle changing email address
        if key != "primary_email_address":
            user[key] = new_values[key]
    if users_db.update_user(user):
        return user["pk"]
    else:
        raise Exception("Failed to update user")