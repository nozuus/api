from flask_restplus import fields, Model

user_create_model = Model("UserCreate", {
    'last_name': fields.String,
    'first_name': fields.String,
    'middle_name': fields.String,
    'birthday': fields.String,
    'user_email': fields.String(attribute='pk'),
    'phone_number': fields.String,
    'major': fields.String,
    #'student_id_number': fields.String, No longer tracking this
    #'active_status': fields.String, No longer tracking this
    'other_emails': fields.List(fields.String),
    'role_id': fields.String
})

get_users_model = Model.inherit("GetUsers", user_create_model, {
    "user_id": fields.String
})

user_update_model = Model("UsersUpdate", {
    'last_name':fields.String(default=None),
    'first_name': fields.String(default=None),
    'middle_name': fields.String(default=None),
    'birthday': fields.String(default=None),
    'phone_number': fields.String(default=None),
    'major': fields.String(default=None),
    #'student_id_number': fields.String(default=None), No longer tracking this
    #'active_status': fields.String(default=None), No longer tracking this
    'other_emails': fields.List(fields.String, default=None)
})

enroll_buzzcard_model = Model("EnrollBuzzcard", {
    "gtid": fields.String()
})