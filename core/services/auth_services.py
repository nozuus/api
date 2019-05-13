import core.database.users_db as users_db
from passlib.hash import pbkdf2_sha256 as sha256
from flask_jwt_extended import create_access_token


# def check_login(user_email, password):
#     user = users_db.get_user_by_email(user_email)
#     if user is None or user["hashed_password"] is None:
#         return False
#     else:
#         if sha256.verify(password, user["hashed_password"]):
#             token = create_access_token(identity=user["user_id"])
#             return token
#         return False
#
#
# def set_password(user_id, password):
#     user = users_db.get_user_by_id(user_id)
#     user["hashed_password"] = sha256.hash(password)
#     if users_db.update_user(user):
#         return
#     else:
#         raise Exception("Failed to create user")