from flask import request
from flask_restplus import Namespace, Resource, fields
import core.services.email_list_service as email_list_service
import core.database.email_list_db as email_list_db
from api.models.email_list_model import get_list_model, subscribe_model, list_model, role_permissions_model, get_role_permission_model


api = Namespace('email_list', description='Email related operations')

api.models[subscribe_model.name] = subscribe_model
api.models[get_list_model.name] = get_list_model
api.models[list_model.name] = list_model
api.models[role_permissions_model.name] = role_permissions_model
api.models[get_role_permission_model.name] = get_role_permission_model


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


@api.route("/create")
class EmailList(Resource):
    @api.doc("create_email_list")
    @api.expect(list_model)
    def post(self):
        '''Create an email list'''
        body = request.json
        list_id = email_list_service.create_email_list(body)
        return {
            'list_id': str(list_id)
        }


@api.route("<list_id>/rolePermissions/<role_id>")
class RolePermissions(Resource):
    @api.doc("get_role_permissions")
    @api.marshal_with(get_role_permission_model)
    def get(self, list_id, role_id):
        '''Get permissions to an email list for a role'''
        return email_list_service.get_role_permissions_by_role(list_id, role_id)

    @api.doc("update_role_permissions")
    @api.expect(role_permissions_model)
    def post(self, list_id, role_id):
        '''Create or update permissions to an email list for a role'''
        body = request.json
        return email_list_service.update_role_permissions(list_id, role_id, body)


@api.route("<list_id>/rolePermissions/")
class RolePermissionsList(Resource):
    @api.doc("get_all_role_permissions")
    @api.marshal_list_with(get_role_permission_model)
    def get(self, list_id):
        '''Get all role permissions for an email list'''
        return email_list_service.get_role_permissions(list_id)


@api.route('/<id>/subscribe')
class Subscription(Resource):
    @api.doc('get_user_by_id')
    @api.expect(subscribe_model)
    def post(self, id):
        '''Add someone to an email list'''
        body = request.json
        email_list_service.add_to_list(id, body["user_id"])
        return "Success"
