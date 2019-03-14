from flask import request
from flask_restplus import Namespace, Resource
import core.database.users_db as users_db
import core.services.users_service as users_service
from api.models.users_model import user_create_model, user_update_model, get_users_model
from flask_jwt_extended import jwt_required

api = Namespace('users', description='User related operations')

api.models[user_create_model.name] = user_create_model
api.models[user_update_model.name] = user_update_model
api.models[get_users_model.name] = get_users_model

@api.route('/<id>')
class User(Resource):
    @api.doc('get_user_by_id')
    @api.marshal_with(get_users_model)
    #@jwt_required
    def get(self, id):
        '''Fetch a user given it's id'''
        user = users_db.get_user_by_id(id)
        return user

    @api.doc('update_user')
    @api.expect(user_update_model)
    #@jwt_required
    def put(self, id):
        '''Updates the user and returns the user_id'''
        body = request.json
        user_id = users_service.update_user(id, body)
        return {
            'user_id': user_id
        }


@api.route("/create")
class UserCreate(Resource):
    @api.doc("create_user")
    @api.expect(user_create_model)
    #@jwt_required
    def post(self):
        '''Create a new user and retrieve the new user_id'''
        body = request.json
        user_id = users_service.create_user(body)
        return {
            'user_id': str(user_id)
        }


@api.route("/")
class UserList(Resource):
    @api.doc('get_all_users')
    @api.marshal_list_with(get_users_model)
    #@jwt_required
    def get(self):
        '''Fetch all users'''
        users = users_db.get_all_users()
        return users