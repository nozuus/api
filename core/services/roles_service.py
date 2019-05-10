import core.database.roles_db as roles_db
import uuid


# def create_role(role):
#     role_id = str(uuid.uuid4())
#     role["role_id"] = role_id
#     if roles_db.create_role(role):
#         return str(role_id)
#     else:
#         raise Exception("Failed to create role")
#
#
# def update_role(role_id, description):
#     role = roles_db.get_role_by_id(role_id)
#     old_role = {
#         "role_id": role_id,
#         "role_description": role["role_description"]
#     }
#     role["role_description"] = description
#     if roles_db.delete_role(old_role) and roles_db.create_role(role):
#         return role["role_id"]
#     else:
#         raise Exception("Failed to create user")