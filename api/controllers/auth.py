from flask import request
from flask_restplus import Namespace, Resource, fields
import pyjwt

api = Namespace('auth', description='Authentication related operations')

@api.route("/login")
class LoginResource(Resource):
    @api.doc("login")
    def post(self):
        '''Login a user. Returns a JWT'''
        body = request.json
