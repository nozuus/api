import core.database.config_db as config_db
from flask_jwt_extended import get_jwt_claims, verify_jwt_in_request

def get_user_permission_names(user_email):
    permissions = config_db.get_permissions_for_user(user_email)

    return [permission["sk"][11:] for permission in permissions]


def check_permissions(required_permissions):
    verify_jwt_in_request()
    claims = get_jwt_claims()
    user_permissions = claims["permissions"]
    if "full_admin" in user_permissions or len(list(set(user_permissions) & set(required_permissions))) > 0:
        return True
    return False

