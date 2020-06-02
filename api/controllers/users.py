from flask import request
from flask_restplus import Namespace, Resource
import core.database.users_db as users_db
import core.services.users_service as users_service
from api.models.users_model import user_create_model, user_update_model, get_users_model, enroll_buzzcard_model
from flask_jwt_extended import jwt_required
from api.permissions_decorator import check_permissions

api = Namespace('users', description='User related operations')

api.models[user_create_model.name] = user_create_model
api.models[user_update_model.name] = user_update_model
api.models[get_users_model.name] = get_users_model
api.models[enroll_buzzcard_model.name] = enroll_buzzcard_model

@api.route('/<user_email>')
class User(Resource):
    @api.doc('get_user_by_username')
    @api.marshal_with(get_users_model)
    @jwt_required
    def get(self, user_email):
        '''Fetch a user given it's email'''
        user = users_db.get_user_by_email(user_email)
        return user

    @api.doc('update_user')
    @api.expect(user_update_model)
    @jwt_required
    def put(self, user_email):
        '''Updates the user and returns the user's email'''
        body = request.json
        user_id = users_service.update_user(user_email, body)
        return {
            'user_email': user_id
        }

    @api.doc('delete_user')
    @jwt_required
    @check_permissions()
    def delete(self, user_email):
        '''Deletes a user given its email'''
        deleted = users_service.delete_user(user_email)
        if deleted:
            return {
                'user_email': user_email
            }
        return { 'error': 'Unable to delete user' }


@api.route("/<user_email>/role")
class UserRoleResource(Resource):
    @api.doc("get_user_role")
    @jwt_required
    def get(self, user_email):
        '''Get a user's role'''
        role = users_service.get_user_role(user_email)
        if role:
            return role
        return {"error": "Unable to load user role"}


@api.route("/<user_email>/permissions")
class UserPermissionsResource(Resource):
    @api.doc("get_user_permissions")
    @jwt_required
    def get(self, user_email):
        '''Get a user's permissions'''
        permissions = users_service.get_user_permissions(user_email)
        return permissions


@api.route("/create")
class UserCreate(Resource):
    @api.doc("create_user")
    @api.expect(user_create_model)
    @jwt_required
    def post(self):
        '''Create a new user'''
        body = request.json
        users_service.create_user(body)
        return {
            'error': "success"
        }


@api.route("/")
class UserList(Resource):
    @api.doc('get_all_users')
    @api.marshal_list_with(get_users_model)
    @jwt_required
    def get(self):
        '''Fetch all users'''
        users = users_db.get_all_users()
        return users


@api.route("/<user_email>/buzzcard")
class EnrollBuzzcard(Resource):
    @api.doc("set_users_buzzcard")
    @api.expect(enroll_buzzcard_model)
    @jwt_required
    @check_permissions("full_admin")
    def post(self, user_email):
        '''Enroll a user's buzzcard for attendance taking'''
        try:
            body = request.json
            result = users_service.enroll_buzzcard(user_email, body["gtid"])
            if result:
                return {"error": "Success"}
            raise Exception("Unable to enroll user buzzcard")
        except Exception as e:
            return {
                "error": "Error enrolling user buzzcard: " + str(e)
            }
