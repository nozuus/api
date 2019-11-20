import core.database.users_db as users_db
import core.database.email_list_db as email_list_db
import core.database.roles_db as roles_db
import uuid
import hashlib


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
            if new_values[key] == "":
                user[key] = None
            else:
                user[key] = new_values[key]
    if users_db.update_user(user):
        return user["pk"]
    else:
        raise Exception("Failed to update user")


def get_user_role(user_email):
    user_role = roles_db.get_role_by_user(user_email)

    if user_role:
        role = roles_db.get_role_by_id(user_role["sk"])
        if role:
            return {
                "role_id": role["pk"],
                "role_description": role["role_description"]
            }
    return None


def get_user_permissions(user_email):
    raw_permissions = users_db.get_user_permissions(user_email)

    user_permissions = [permission["sk"][11:] for permission in raw_permissions]

    return user_permissions


def enroll_buzzcard(user_email, gtid):
    user = users_db.get_user_by_email(user_email)

    if user is None:
        raise Exception("Invalid user email")

    hashed = hash_gtid(gtid)

    existing_hash = users_db.get_existing_gtid(user_email)

    if existing_hash is not None:
        users_db.delete_item(existing_hash["pk"], existing_hash["sk"])

    item = {
        "pk": user_email,
        "sk": "gtid_" + hashed
    }
    return users_db.put_item_no_check(item)


def get_user_by_gtid(gtid):
    hashed = hash_gtid(gtid)

    user_email = users_db.get_user_by_gtid(hashed)

    if user_email is None:
        raise Exception("Invalid GTID")
    return user_email

def hash_gtid(gtid):
    return hashlib.sha512(str(gtid).encode('utf-8')).hexdigest()