from flask import request
from flask_restplus import Namespace, Resource, fields
import core.services.auth_services as auth_services
from api.models.auth_model import login_model, set_password_model


api = Namespace('auth', description='Authentication related operations')

api.models[login_model.name] = login_model
api.models[set_password_model.name] = set_password_model


@api.route("/login")
class LoginResource(Resource):
    @api.doc("login")
    @api.expect(login_model)
    def post(self):
        '''Login a user.
        Returns a JWT for the user to use for future requests.'''
        body = request.json
        user_email = body["user_email"]
        password = body["password"]
        token = auth_services.check_login(user_email, password)
        if token is not False:
            return token
        return "Invalid"


@api.route("/updatePassword")
class UpdatePasswordResource(Resource):
    @api.doc("update_password")
    @api.expect(set_password_model)
    def post(self):
        '''Updates a user's password password given a password reset token.'''
        body = request.json
        user_id = body["user_id"]
        user_password = body["password"]
        auth_services.set_password(user_id, user_password)
        return "Success";