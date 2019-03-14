from flask import request
from flask_restplus import Namespace, Resource, fields
import core.services.email_list_service as email_list_service
import core.database.email_list_db as email_list_db
from api.models.email_list_model import get_list_model, subscribe_model, list_model


api = Namespace('email_list', description='Email related operations')

api.models[subscribe_model.name] = subscribe_model
api.models[get_list_model.name] = get_list_model
api.models[list_model.name] = list_model


@api.route("/")
class EmailLists(Resource):
    @api.doc("get_all_email_lists")
    @api.marshal_list_with(get_list_model)
    def get(self):
        '''Get all email lists'''
        lists = email_list_db.get_all_email_lists()
        return lists


@api.route("/<id>")
class EmailList(Resource):
    @api.doc("get_email_list_by_id")
    @api.marshal_with(get_list_model)
    def get(self, id):
        '''Get email list by id'''
        list = email_list_db.get_email_list_by_id(id)
        return list


@api.route('/<id>/subscribe')
class Subscription(Resource):
    @api.doc('get_user_by_id')
    @api.expect(subscribe_model)
    def post(self, id):
        '''Add someone to an email list'''
        body = request.json
        email_list_service.add_to_list(id, body["user_id"])
        return "Success"
