import core.database.config_db as config_db
import core.database.db as base_db
import core.database.users_db as users_db
from flask_jwt_extended import get_jwt_claims, verify_jwt_in_request


def get_user_permission_names(user_email):
    permissions = config_db.get_permissions_for_user(user_email)
    permission_names = [permission["sk"][11:] for permission in permissions]

    # Check if user has any permissions and apply those as well
    positions = get_positions_for_user(user_email)
    for position in positions:
        for permission in position["permissions"]:
            if permission not in permission_names:
                permission_names.append(permission)
    return permission_names


def check_permissions(required_permissions):
    verify_jwt_in_request()
    claims = get_jwt_claims()
    user_permissions = claims["permissions"]
    if "full_admin" in user_permissions or len(list(set(user_permissions) & set(required_permissions))) > 0:
        return True
    return False


def get_settings():
    settings = config_db.get_settings()
    to_return = []
    for setting in settings:
        if check_permissions(setting["permissions"]):
            to_return.append(setting)

    return to_return


def get_setting_by_identifer(identifier):
    if "setting" not in identifier:
        identifier = "setting_" + identifier
    setting = config_db.get_item("config", identifier)

    if setting is None:
        raise Exception("Invalid identifier")

    return setting


def create_setting(setting):
    setting["pk"] = "config"
    setting["sk"] = "setting_" + setting["identifier"]

    return config_db.put_item_no_check(setting)


def create_permission(permission) :
    permission["pk"] = "config"
    permission["sk"] = "permission_%s" % permission["name"]


    if base_db.put_item_no_check(permission) :
        return
    else:
        raise Exception("Unable to create permission")


def get_positions_for_user(user_email):
    user = users_db.get_user_by_email(user_email)
    if user is None:
        raise Exception("Invalid user email")

    positions_held = base_db.get_items_by_type("position_holder_%s" % user_email)
    positions = []
    for position_held in positions_held:
        position = base_db.get_item(position_held["pk"], "position")
        positions.append(position)

    return positions
