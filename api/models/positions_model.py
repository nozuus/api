from flask_restplus import fields, Model

position_model = Model("Position", {
    'name': fields.String,
    'description': fields.String,
    'permissions': fields.List(fields.String),
    'email_address': fields.String(default=None)
})


get_position_model = Model.inherit("GetPosition", position_model, {
    'id': fields.String(attribute='pk')
})
