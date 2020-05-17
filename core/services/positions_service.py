import core.database.db as base_db
import core.database.email_list_db as email_list_db
import core.services.email_list_service as email_list_service
import core.database.users_db as users_db
import uuid


def create_position(position):
    position_id = "position_%s" % str(uuid.uuid4())[:8]
    position["pk"] = position_id
    position["sk"] = "position"
    if len(position["permissions"]) > 0:
        all_permissions_objects = \
            base_db.get_items_for_pk_by_type("config", "permission")
        all_permissions = [obj["sk"] for obj in all_permissions_objects]
        for permission in position["permissions"]:
            formatted = "permission_%s" % permission
            if formatted not in all_permissions:
                raise Exception("Invalid permission")
    if position["email_address"] is not None:
        email_list = email_list_db.get_email_list_by_address(position["email_address"])
        if email_list:
            email_list["position"] = position_id
            base_db.put_item_no_check(email_list)
        else:
            email_list = {
                "address": position["emailAddress"],
                "subject_prefix": None,
                "description": "Email address for position: %s" %position["name"],
                "allow_external": True,
                "position": position_id
            }
            email_list_service.create_email_list(email_list);
    if base_db.put_item_unique_pk(position):
        return str(position_id)
    else:
        raise Exception("Failed to create position")


def get_position(position_id):
    position = base_db.get_item(position_id, "position")
    return position


def get_all_positions():
    positions = base_db.get_items_by_type("position")
    return positions


def add_user_to_position(position_id, user_email):
    position = get_position(position_id)
    user = users_db.get_user_by_email(user_email)
    if position is None:
        raise Exception("Invalid position id")
    if user is None:
        raise Exception("Invalid user id")

    itemObj = {
        "pk": position_id,
        "sk": "position_holder_%s" % user_email
    }

    if base_db.put_item_no_check(itemObj):
        return
    else:
        raise Exception("Error adding user to position")


def remove_user_from_position(position_id, user_email):
    position = get_position(position_id)
    user = users_db.get_user_by_email(user_email)
    if position is None:
        raise Exception("Invalid position id")
    if user is None:
        raise Exception("Invalid user id")

    if base_db.delete_item(position_id, "position_holder_%s" % user_email):
        return
    else:
        raise Exception("Error adding user to position")


def get_users_for_position(position_id):
    position = get_position(position_id)

    if position is None:
        raise Exception("Invalid position id")

    user_objects = base_db.get_items_for_pk_by_type(position_id, "position_holder")
    users = [user["sk"][16:] for user in user_objects]
    return users
