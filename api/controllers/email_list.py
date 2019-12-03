from flask import request
from flask_restplus import Namespace, Resource, fields
import core.services.email_list_service as email_list_service
import core.services.emailer_service as emailer_service
import core.database.email_list_db as email_list_db
from api.models.email_list_model import subscribe_model, list_model, role_permissions_model, get_role_permission_model, update_list_model
from flask_jwt_extended import jwt_required
from api.permissions_decorator import check_permissions


api = Namespace('email_list', description='Email related operations')

api.models[subscribe_model.name] = subscribe_model
api.models[list_model.name] = list_model
api.models[role_permissions_model.name] = role_permissions_model
api.models[get_role_permission_model.name] = get_role_permission_model
api.models[update_list_model.name] = update_list_model


@api.route("/")
class EmailLists(Resource):
    @api.doc("get_all_email_lists")
    @api.marshal_list_with(list_model)
    @jwt_required
    def get(self):
        '''Get all email lists'''
        args = request.args
        if "onlyJoinable" in args and args["onlyJoinable"] in ["True", "true"]:
            lists = email_list_service.get_joinable_lists()
        else:
            lists = email_list_db.get_all_email_lists()
        return lists


@api.route("/<address>")
class EmailList(Resource):
    @api.doc("get_email_list_by_id")
    @api.marshal_with(list_model)
    @jwt_required
    def get(self, address):
        '''Get email list by address'''
        email_list = email_list_db.get_email_list_by_address(address)
        return email_list

    @api.doc("update_list_by_id")
    @api.expect(update_list_model)
    @jwt_required
    @check_permissions("can_manage_email_lists")
    def put(self, address):
        '''Update the details of an email list'''
        email_list = request.json
        email_list["pk"] = address
        email_list["sk"] = "list"
        result = email_list_db.put_item_no_check(email_list)
        if result:
            return {"error": "Success"}
        return {"error": "Unable to save email list details"}


@api.route("/create")
class EmailList(Resource):
    @api.doc("create_email_list")
    @api.expect(list_model)
    @jwt_required
    @check_permissions("can_manage_email_lists")
    def post(self):
        '''Create an email list'''
        body = request.json
        address = body["address"]
        email_list_service.create_email_list(body)
        return {
            'address': address
        }


@api.route("/requestVerification")
class RequestVerification(Resource):
    @api.doc("request_verification")
    @api.expect(subscribe_model)
    @jwt_required
    def post(self):
        '''Request an email verification'''
        body = request.json
        address = body["user_email"]
        emailer_service.verify_email_address(address)
        return {
            "error": "Success"
        }


@api.route("/checkVerification")
class CheckVerification(Resource):
    @api.expect(subscribe_model)
    @jwt_required
    def post(self):
        body = request.json
        address = body["user_email"]
        return {
            "verified": emailer_service.check_verification(address)
        }


@api.route("/<address>/rolePermissions/<role_id>")
class RolePermissions(Resource):
    @api.doc("get_role_permissions")
    @api.marshal_with(get_role_permission_model)
    def get(self, address, role_id):
        '''Get permissions to an email list for a role'''
        permissions = email_list_db.get_role_permissions_by_role(address, role_id)
        return permissions

    @api.doc("set_role_permissions")
    @api.expect(role_permissions_model)
    def post(self, address, role_id):
        '''Create or update permissions to an email list for a role'''
        body = request.json
        return email_list_service.update_role_permissions(address, role_id, body)


@api.route("/<address>/rolePermissions/")
class RolePermissionsList(Resource):
    @api.doc("get_all_role_permissions")
    @api.marshal_list_with(get_role_permission_model)
    def get(self, address):
        '''Get all role permissions for an email list'''
        permissions = email_list_db.get_role_permissions(address)
        return permissions


@api.route('/<address>/subscribe')
class Subscription(Resource):
    @api.doc('get_user_by_id')
    @api.expect(subscribe_model)
    def post(self, address):
        '''Add someone to an email list'''
        body = request.json
        result, permission = email_list_service.add_to_list(address, body["user_email"])
        if not result:
            return {
                "error": "Missing Permission",
                "permission": permission
            }
        return {"error": "Success"}


@api.route("/<address>/subscribers")
class Subscribers(Resource):
    @api.doc("get_users_on_list")
    def get(self, address):
        users = email_list_db.get_users_on_list(address)
        emails = [user["pk"] for user in users]
        return emails


@api.route("/<address>/subscribers/<user_email>")
class RemoveSubscribers(Resource):
    @api.doc("remove_user_from_list")
    def delete(self, address, user_email):
        email_list_service.delete_subscription(address, user_email)
        return {"error": "Success"}


@api.route("/subscriptions/<user_email>")
class Subscriptions(Resource):
    @api.doc("get_user_subscriptions")
    @api.marshal_list_with(list_model)
    @jwt_required
    def get(self, user_email):
        '''Get the lists a user is subscribed to'''
        subscriptions = email_list_service.get_subscriptions(user_email)
        return subscriptions
