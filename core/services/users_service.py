import core.database.users_db as users_db
import uuid


def create_user(user):
    user_id = uuid.uuid4()
    user["user_id"] = user_id
    if users_db.create_user(user):
        return str(user_id)
    else:
        raise Exception("Failed to create user")
