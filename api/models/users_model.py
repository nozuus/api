from flask_restplus import fields, Model

user_create_model = Model("UserCreate", {
    'last_name': fields.String,
    'first_name': fields.String,
    'middle_name': fields.String,
    'birthday': fields.String,
    'primary_email_address': fields.String,
    'secondary_email_address': fields.String,
    'phone_number': fields.String,
    'major': fields.String,
    'student_id_number': fields.String,
    'active_status': fields.String,
})

get_users_model = Model.inherit("GetUsers", user_create_model, {
    "user_id": fields.String
})

user_update_model = Model("UsersUpdate", {
    'last_name':fields.String(default=None),
    'first_name': fields.String(default=None),
    'middle_name': fields.String(default=None),
    'birthday': fields.String(default=None),
    'primary_email_address': fields.String(default=None),
    'secondary_email_address': fields.String(default=None),
    'phone_number': fields.String(default=None),
    'major': fields.String(default=None),
    'student_id_number': fields.String(default=None),
    'active_status': fields.String(default=None),
})