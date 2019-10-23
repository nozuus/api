from flask_restplus import fields, Model

subscribe_model = Model("SubscribeToList", {
    'user_email': fields.String,
})


list_model = Model("EmailList", {
    "address": fields.String(attribute="pk"),
    "subject_prefix": fields.String,
    "description": fields.String,
    "allow_external": fields.Boolean
})

update_list_model = Model("UpdateEmailList", {
    "subject_prefix": fields.String,
    "description": fields.String,
    "allow_external": fields.Boolean
})


role_permissions_model = Model("RolePermissions", {
    "can_self_join": fields.Boolean,
    "can_be_invited": fields.Boolean,
    "joined_on_creation": fields.Boolean,
    "default": fields.Boolean,
})


class RolePermissionParser(fields.String):
    def format(self, value):
        if "permission" in value:
            return value[11:]
        return value


get_role_permission_model = Model.inherit("GetRolePermissions", role_permissions_model, {
    "role_id": RolePermissionParser(attribute="sk")
})