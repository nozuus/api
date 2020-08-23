from flask import request
from flask_restplus import Namespace, Resource, fields
from api.permissions_decorator import check_permissions
from flask_jwt_extended import jwt_required
from flask_restplus import fields, Model
import core.services.admin_service as admin_service

semester_launch_model = Model("SemesterLaunch", {
    'semester_start_date': fields.Date,
    'semester_end_date': fields.Date,
    'semester_description': fields.String,
    'other_variables': fields.Raw
})

api = Namespace('admin', description='Admin related operations')
api.models[semester_launch_model.name] = semester_launch_model


@api.route("/semesterLaunch")
class SemesterLaunchResource(Resource):
    @jwt_required
    @check_permissions("full_admin")
    @api.expect(semester_launch_model)
    def post(self):
        body = request.json
        admin_service.launch_semester(body)
        return { "error": "Success" }
