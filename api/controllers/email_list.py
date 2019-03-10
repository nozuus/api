from flask import request
from flask_restplus import Namespace, Resource, fields
import core.database.email_list_db as email_db
import core.database.users_db as users_db
import core.services.users_service as users_service

api = Namespace('email_list', description='Email related operations')


@api.route('/newSubscription')
class User(Resource):
    @api.doc('get_user_by_id')
    def post(self):
        '''Add someone to an email list'''
        body = request.json
        listInfo = email_db.get_email_list(body["prefix"], body["domain"])
        email_db.add_to_list(body["user_id"], listInfo["list_id"])
        return body["user_id"] + " successfully added to the email list " + listInfo["prefix"]
