from flask import request
from flask_restplus import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
import core.services.auth_services as auth_services

api = Namespace('auth', description='Authentication related operations')


@api.route("/login")
class LoginResource(Resource):
    @api.doc("login")
    def post(self):
        '''Login a user. Returns a JWT'''
        body = request.json
        user_id = body["user_id"]
        token = create_access_token(identity=user_id)
        return token


@api.route("/updatePassword")
class UpdatePasswordResource(Resource):
    @api.doc("update_password")
    def post(self):
        '''Updates a user's password'''
        body = request.json
        user_id = body["user_id"]
        user_password = body["password"]
        auth_services.set_password(user_id, user_password)
        return "Success";