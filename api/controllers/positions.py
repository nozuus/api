from flask import request
from flask_restplus import Namespace, Resource, fields
from api.models.positions_model import position_model, get_position_model
from flask_jwt_extended import jwt_required
from api.permissions_decorator import check_permissions
import core.services.positions_service as positions_service


api = Namespace('positions', description='Positions related operations')

api.models[position_model.name] = position_model
api.models[get_position_model.name] = get_position_model

@api.route("/create")
class PositionCreate(Resource):
    @api.doc("create_position")
    @api.expect(position_model)
    @jwt_required
    @check_permissions("can_manage_positions")
    def post(self):
        '''Create a new position'''
        body = request.json
        position_id = positions_service.create_position(body)
        return {
            'error': "success",
            'position_id': position_id
        }


@api.route("/<position_id>")
class Position(Resource):
    @api.doc("get_position")
    @jwt_required
    @api.marshal_with(get_position_model)
    def get(self, position_id):
        '''Get Position by id'''
        position = positions_service.get_position(position_id)
        return position

    @api.doc("update_position")
    @jwt_required
    @api.expect(get_position_model)
    @check_permissions("can_manage_permissions")
    def put(self, position_id):
        '''Update position'''
        position = request.json
        positions_service.update_position(position_id, position)
        return {
            'error': "Success"
        }


@api.route("/")
class PositionsList(Resource):
    @api.doc("get_all_positions")
    @jwt_required
    @api.marshal_list_with(get_position_model)
    def get(self):
        '''Get all positions'''
        positions = positions_service.get_all_positions()
        return positions


@api.route("/<position_id>/users/<user_email>")
class AddUser(Resource):
    @api.doc("add_user_to_position")
    @jwt_required
    @check_permissions("can_manage_position")
    def post(self, position_id, user_email):
        '''Add user to position'''
        positions_service.add_user_to_position(position_id, user_email)
        return {
            "error": "success"
        }

    @api.doc("remove_user_from_position")
    @jwt_required
    @check_permissions("can_manage_position")
    def delete(self, position_id, user_email):
        '''Remove user from position'''
        positions_service.remove_user_from_position(position_id, user_email)
        return {
            "error": "success"
        }


@api.route("/<position_id>/users/")
class GetUsers(Resource):
    @api.doc("get_users_for_position")
    @jwt_required
    def get(self, position_id):
        '''Get users for position'''
        users = positions_service.get_users_for_position(position_id)
        return users
