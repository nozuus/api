import core.database.email_list_db as email_list_db
import core.database.users_db as users_db
import core.database.email_list_db as email_db
import uuid


def add_to_list(address, user_email):
    # make sure that user and email list are both valid before adding
    user = users_db.get_user_by_email(user_email)
    email_list = email_list_db.get_email_list_by_address(address)
    if user and email_list:
        email_list_db.add_to_list(address, user_email)


def create_email_list(email_list):
    email_list["sk"] = "list"
    email_list["pk"] = email_list.pop("address")
    if email_db.create_email_list(email_list):
        return True
    else:
        raise Exception("Failed to create email list")

#
# def get_role_permissions(list_id):
#     email_list = email_list_db.get_email_list_by_id(list_id)
#     if email_list is None or "role_permissions" not in email_list:
#         return []
#     return email_list["role_permissions"]
#


def update_role_permissions(address, role_id, permissions):
    role_permission = permissions
    role_permission["pk"] = address
    role_permission["sk"] = "permission_%s" % role_id
    if email_db.save_role_permissions(role_permission):
        return True
    else:
        raise Exception("Failed to save role permission")
