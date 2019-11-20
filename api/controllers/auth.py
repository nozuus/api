from flask import request
from flask_restplus import Namespace, Resource, fields
import core.services.auth_services as auth_services
from api.models.auth_model import login_model, set_password_model, request_reset_model, reset_password_model, change_password_model


api = Namespace('auth', description='Authentication related operations')

api.models[login_model.name] = login_model
api.models[set_password_model.name] = set_password_model
api.models[request_reset_model.name] = request_reset_model
api.models[reset_password_model.name] = reset_password_model
api.models[change_password_model.name] = change_password_model


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
        user_email = body["user_email"]
        user_password = body["new_password"]
        auth_services.set_password(user_email, user_password)
        return "Success"


@api.route("/changePassword")
class ChangePasswordResource(Resource):
    @api.doc("change_password")
    @api.expect(change_password_model)
    def post(self):
        body = request.json
        user_email = body["user_email"]
        new_password = body["new_password"]
        old_password = body["old_password"]
        result = auth_services.change_password(user_email, old_password, new_password)
        if result:
            return {"error": "Success"}
        return {"error": "Invalid old password"}


@api.route("/checkLoginStatus")
class CheckLoginResource(Resource):
    @api.doc("check_login_status")
    def get(self):
        '''Verifies the users' bearer token'''
        try:
            identity = auth_services.get_identity()
            return {
                "user_name": identity
            }
        except:
            return None


@api.route("/requestResetPassword")
class RequestResetPasswordResource(Resource):
    @api.doc("request_password_reset")
    @api.expect(request_reset_model)
    def post(self):
        '''Request a password reset email for a user'''
        body = request.json
        result = auth_services.request_password_reset(body["user_email"])
        if result:
            return {"error": "Success"}
        else:
            return {"error": "Unable to request password reset"}


@api.route("/resetPassword")
class ResetPasswordResource(Resource):
    @api.doc("reset_password")
    @api.expect(reset_password_model)
    def post(self):
        '''Reset a user's password given a reset token'''
        body = request.json
        result = auth_services.reset_password(body["user_email"], body["token"], body["password"])
        if result:
            return {"error": "Success"}
        else:
            return {"error": "Unable to reset user password"}