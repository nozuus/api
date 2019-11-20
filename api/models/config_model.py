from flask_restplus import fields, Model

permission_model = Model("Permissions", {
    'name': fields.String,
    'description': fields.String,
})

setting_model = Model("Setting", {
    'identifier': fields.String(),
    'description': fields.String,
    'value': fields.Raw,
    'permissions': fields.List(fields.String)
})