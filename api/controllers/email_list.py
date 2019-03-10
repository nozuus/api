from flask import request
from flask_restplus import Namespace, Resource, fields
import core.services.email_list_service as email_list_service

api = Namespace('email_list', description='Email related operations')


@api.route('/newSubscription')
class User(Resource):
    @api.doc('get_user_by_id')
    def post(self):
        '''Add someone to an email list'''
        body = request.json
        email_list_service.add_to_list(body["user_id"], body["prefix"],
                                       body["domain"])
        return "Success"
