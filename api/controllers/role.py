from flask import request
from flask_restplus import Namespace, Resource
from api.models.roles_model import role_model, get_role_model, add_user_model
import core.database.roles_db as roles_db
import core.services.roles_service as roles_service
from flask_jwt_extended import jwt_required

api = Namespace('role', description='Role related operations')

api.models[get_role_model.name] = get_role_model
api.models[role_model.name] = role_model
api.models[add_user_model.name] = add_user_model


@api.route('/<id>')
class Role(Resource):
    @api.doc('get_role_by_id')
    @api.marshal_with(get_role_model)
    #@jwt_required
    def get(self, id):
        '''Fetch a role given it's id'''
        role = roles_db.get_role_by_id(id)
        return role

    @api.doc('update_role')
    @api.expect(role_model)
    #@jwt_required
    def put(self, id):
        '''Updates the role and returns the role_id'''
        body = request.json
        role_id = roles_service.update_role(id, body)
        return {
            'role_id': role_id
        }


@api.route("/<id>/users")
class RoleUsers(Resource):
    @api.doc("get_users_with_role")
    def get(self, id):
        '''Get all users that have a given role'''
        user_entries = roles_db.get_users_by_role(id)
        users = []
        for user in user_entries:
            users.append(user["pk"])
        return users

    @api.doc("add_user_to_role")
    @api.expect(add_user_model)
    def post(self, id):
        '''Add a user to a role.
        Will update an existing role if the user has one.'''
        body = request.json
        roles_service.remove_existing_role(body["user_email"])
        result = roles_db.set_user_role(body["user_email"], id)
        if result:
            return {"error": "Success"}
        return {"error": "Unable to set user role"}



@api.route("/create")
class RoleCreate(Resource):
    @api.doc("create_role")
    @api.expect(role_model)
    #@jwt_required
    def post(self):
        '''Create a new role and retrieve the new role_id'''
        body = request.json
        role_id = roles_service.create_role(body)
        return {
            'role_id': str(role_id)
        }


@api.route("/")
class RoleList(Resource):
    @api.doc('get_all_users')
    @api.marshal_list_with(get_role_model)
    #@jwt_required
    def get(self):
        '''Fetch all roles'''
        roles = roles_db.get_all_roles()
        return roles
