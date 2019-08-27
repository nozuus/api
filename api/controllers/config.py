from flask import request
from flask_restplus import Namespace, Resource, fields
from api.models.config_model import permission_model
import core.database.config_db as config_db
from flask_jwt_extended import jwt_required

api = Namespace('config', description='Config related operations')

api.models[permission_model.name] = permission_model

@api.route("/permissions")
class PermissionsResource(Resource):
    @api.doc("get_permissions")
    @api.marshal_list_with(permission_model)
    @jwt_required
    def get(self):
        '''Get all valid permissions'''
        try:
            permissions = config_db.get_permissions()
            return permissions
        except Exception as e:
            return {
                "error" : "Error fetching permissions: " + str(e)
            }
