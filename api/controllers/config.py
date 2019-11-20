from flask import request
from flask_restplus import Namespace, Resource, fields
from api.models.config_model import permission_model, setting_model
import core.database.config_db as config_db
import core.services.config_service as config_service
from flask_jwt_extended import jwt_required

api = Namespace('config', description='Config related operations')

api.models[permission_model.name] = permission_model
api.models[setting_model.name] = setting_model

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


@api.route("/settings")
class SettingsResource(Resource):
    @api.doc("get_all_settings")
    @api.marshal_list_with(setting_model)
    @jwt_required
    def get(self):
        settings = config_service.get_settings()
        return settings

    @api.doc("create_setting")
    @api.expect(setting_model)
    @jwt_required
    def post(self):
        body = request.json
        config_service.create_setting(body)
        return {"error": "Success"}


@api.route("/settings/<identifier>")
class GetSettingResource(Resource):
    @api.marshal_with(setting_model)
    @jwt_required
    def get(self, identifier):
        setting = config_service.get_setting_by_identifer(identifier)
        return setting
