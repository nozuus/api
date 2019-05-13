from flask_restplus import fields, Model

role_model = Model("Role", {
    'role_description': fields.String,
})


get_role_model = Model.inherit("GetRole", role_model, {
    "role_id": fields.String(attribute="pk")
})