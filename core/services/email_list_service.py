import core.database.email_list_db as email_list_db
import core.database.users_db as users_db
import core.database.email_list_db as email_db
import uuid


def add_to_list(list_id, user_id):
    user = users_db.get_user_by_id(user_id)
    primary_email = user["primary_email_address"]
    list_id = email_db.get_email_list_by_id(list_id)["list_id"]
    subscription = {
        "user_id": user_id,
        "list_id": list_id,
        "user_primary_email_address": primary_email
    }
    email_list_db.add_to_list(subscription)


def create_email_list(email_list):
    list_id = str(uuid.uuid4())
    email_list["list_id"] = list_id
    if email_db.create_email_list(email_list):
        return str(list_id)
    else:
        raise Exception("Failed to create email list")


def get_role_permissions(list_id):
    email_list = email_list_db.get_email_list_by_id(list_id)
    if email_list is None or "role_permissions" not in email_list:
        return []
    return email_list["role_permissions"]


def get_role_permissions_by_role(list_id, role_id):
    email_list = email_list_db.get_email_list_by_id(list_id)
    if email_list is None or "role_permissions" not in email_list:
        return None
    for permission in email_list["role_permissions"]:
        if permission["role_id"] == role_id:
            return permission
    return None


def update_role_permissions(list_id, role_id, new_permissions):
    email_list = email_list_db.get_email_list_by_id(list_id)
    permission_found = False
    if "role_permissions" not in email_list:
        email_list["role_permissions"] = []
    for permission, index in email_list["role_permissions"]:
        if permission["role_id"] == role_id:
            permission["role_id"]["can_self_join"] = new_permissions["can_self_join"]
            permission["role_id"]["can_be_invited"] = new_permissions["can_be_invited"]
            permission["role_id"]["joined_by_default"] = new_permissions["joined_by_default"]
            permission_found = True
    if not permission_found:
        new_permissions["role_id"] = role_id
        email_list["role_permissions"].append(new_permissions)
    email_list_db.update_email_list(email_list)
    return "Success"
