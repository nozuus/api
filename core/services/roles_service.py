import core.database.roles_db as roles_db
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
        raise Exception("Failed to update user")