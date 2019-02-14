from flask_restplus import Namespace, Resource, fields

api = Namespace('users', description='User related operations')

USERS = ["userId1", "userId2", "userId3"]


@api.route('/<id>')
@api.param('id', 'The user id')
@api.response(404, 'User not found')
class Cat(Resource):
    @api.doc('get_user')
    def get(self, id):
        '''Fetch a user given its id'''
        for userId in USERS:
            if userId == id:
                return userId;
        api.abort(404)