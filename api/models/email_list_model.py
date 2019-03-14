from flask_restplus import fields, Model

subscribe_model = Model("SubscribeToList", {
    'user_id': fields.String,
})


list_model = Model("EmailList", {
    "prefix": fields.String,
    "domain": fields.String,
    "subject_prefix": fields.String,
    "description": fields.String,
    "only_recipients_can_send": fields.Boolean
})


get_list_model = Model.inherit("GetEmailList", list_model, {
    "list_id": fields.String
})


role_permissions_model = Model("RolePermissions", {
    "can_self_join": fields.Boolean,
    "can_be_invited": fields.Boolean,
    "joined_by_default": fields.Boolean,
})

get_role_permission_model = Model.inherit("GetRolePermissions", role_permissions_model, {
    "role_id": fields.String
})