from flask import request
from flask_restplus import Namespace, Resource, fields
import core.database.users_db as users_db
import core.services.users_service as users_service

api = Namespace('users', description='User related operations')

user_model = api.schema_model('User', {
    'properties': {
        'last_name': {
            'type': 'string'
        },
        'first_name': {
            'type': 'string'
        },
        'middle_name': {
            'type': 'string'
        },
        'birthday': {
            'type': 'string',
            'format': 'date-time'
        },
        'primary_email_address': {
            'type': 'string',
            'format': 'email'
        },
        'secondary_email_address': {
            'type': 'string',
            'format': 'email'
        },
        'phone_number': {
            'type': 'string',
            "pattern": "^(\\([0-9]{3}\\))?[0-9]{3}-[0-9]{4}$"
        },
        'major': {
            'type': 'string'
        },
        'student_id_number': {
            'type': 'string'
        },
        'active_status': {
            'type': 'string'
        },
    },
    'type': 'object'
})


@api.route('/<id>')
class User(Resource):
    @api.doc('get_user_by_id')
    def get(self, id):
        '''Fetch a user given it's id'''
        user = users_db.get_user_by_id(id)
        return user


@api.route("/update")
class UserUpdate(Resource):
    @api.doc("update_user")
    def post(self):
        body = request.json
        user_id = body["user_id"]
        user = users_db.get_user_by_id(user_id)
        for key in body:
            user[key] = body[key]
        user_id = users_service.update_user(user)
        return {
            'user_id': user_id
        }

@api.route("/create")
class UserCreate(Resource):
    @api.doc("create_user")
    @api.expect(user_model)
    def post(self):
        '''Create a new user and retrieve the new user_id'''
        body = request.json
        user_id = users_service.create_user(body)
        return {
            'user_id': user_id
        }


@api.route("/")
class UserList(Resource):
    @api.doc('get_all_users')
    def get(self):
        '''Fetch all users'''
        users = users_db.get_all_users()
        return users