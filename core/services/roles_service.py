import core.database.roles_db as roles_db
import core.database.users_db as users_db
import uuid


def create_role(role):
    role_id = "role_%s" % str(uuid.uuid4())[:8]
    role["pk"] = role_id
    role["sk"] = "role"
    if roles_db.create_role(role):
        return str(role_id)
    else:
        raise Exception("Failed to create role")


def update_role(role_id, new_values):
    role = roles_db.get_role_by_id(role_id)
    for key in new_values:
        if key != "role_id":
            role[key] = new_values[key]
    if roles_db.update_role(role):
        return role["pk"]
    else:
        raise Exception("Failed to update role")


def group_users_by_roles():
    roles = roles_db.get_all_roles()

    for role in roles:
        role_id = role["pk"]


def remove_existing_role(user_email):
    user_role = roles_db.get_role_by_user(user_email)
    if user_role is not None:
        return roles_db.delete_item(user_email, user_role["sk"])
    return True


def get_users_without_role():
    users = users_db.get_all_users()
    users_without_role = []
    for user in users:
        if roles_db.get_role_by_user(user["pk"]) is None:
            users_without_role.append(user["pk"])
    return users_without_role


def update_user_role(user_email, role_id):
    user = users_db.get_item(user_email, "user")
    if user is None:
        raise Exception("Invalid user email")
    role = roles_db.get_role_by_id(role_id)
    if role is None:
        raise Exception("Invalid role id")
    remove_existing_role(user_email)
    roles_db.set_user_role(user_email, role_id)

    user["role_id"] = role_id

    users_db.put_item_no_check(user)