import core.database.users_db as users_db
import core.database.email_list_db as email_list_db
import uuid

#
# def create_user(user):
#     user_id = str(uuid.uuid4())
#     user["user_id"] = user_id
#     if users_db.create_user(user):
#         return str(user_id)
#     else:
#         raise Exception("Failed to create user")
#
#
# def update_user(user_id, new_values):
#     user = users_db.get_user_by_id(user_id)
#     for key in new_values:
#         user[key] = new_values[key]
#         if key == "primary_email_address":
#             if not email_list_db.update_user_email(user_id, new_values[key]):
#                 return "Error"
#     if users_db.update_user(user):
#         return user["user_id"]
#     else:
#         raise Exception("Failed to create user")