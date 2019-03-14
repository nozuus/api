from flask_restplus import Model, fields

login_model = Model("Login", {
    "user_email": fields.String,
    "password": fields.String
})

set_password_model = Model("SetPassword", {
    "user_email": fields.String,
    "new_password": fields.String,
    "set_password_token": fields.String
})