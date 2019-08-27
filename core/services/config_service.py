import core.database.config_db as config_db

def get_user_permission_names(user_email):
    permissions = config_db.get_permissions_for_user(user_email)

    return [permission["sk"][11:] for permission in permissions]

