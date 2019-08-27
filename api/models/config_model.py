from flask_restplus import fields, Model

permission_model = Model("Permissions", {
    'name': fields.String,
    'description': fields.String,
})

