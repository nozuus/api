from flask import request
from flask_restplus import Namespace, Resource
from flask_jwt_extended import jwt_required
from api.models.reporting_model import report_create_model, get_report_model, type_create_model, get_type_model, semester_create_model, get_semester_model
import core.services.reporting_service as reporting_service

api = Namespace('reporting', description='Reporting related operations')

api.models[report_create_model.name] = report_create_model
api.models[get_report_model.name] = get_report_model
api.models[type_create_model.name] = type_create_model
api.models[get_type_model.name] = get_type_model
api.models[semester_create_model.name] = semester_create_model
api.models[get_semester_model.name] = get_semester_model

# @api.route('/<user_email>')
# class User(Resource):
#     @api.doc('get_user_by_username')
#     @api.marshal_with(get_users_model)
#     @jwt_required
#     def get(self, user_email):
#         '''Fetch a user given it's email'''
#         user = users_db.get_user_by_email(user_email)
#         return user
#
#     @api.doc('update_user')
#     @api.expect(user_update_model)
#     @jwt_required
#     def put(self, user_email):
#         '''Updates the user and returns the user's email'''
#         body = request.json
#         user_id = users_service.update_user(user_email, body)
#         return {
#             'user_email': user_id
#         }


@api.route("/create")
class ReportCreate(Resource):
    @api.doc("create_report")
    @api.expect(report_create_model)
    @jwt_required
    def post(self):
        '''Create a new report'''
        body = request.json
        try:
            report_id = reporting_service.create_report(body)
            return {"report_id": report_id}
        except Exception as e:
            return {
                'error': "Error creating report: " + str(e)
            }

@api.route("/types/create")
class TypeCreate(Resource):
    @api.doc("create_report_type")
    @api.expect(type_create_model)
    @jwt_required
    def post(self):
        '''Create a new report type'''
        body = request.json
        try:
            if body["value_type"] == "optionselect" and "options" not in body:
                return {"error": "Value type 'optionselect' requires a list of options"}
            report_type_id = reporting_service.create_report_type(body)
            return {"report_type_id": report_type_id}
        except Exception as e:
            return {
                'error': "Error creating report type: " + str(e)
            }


@api.route("/semesters/create")
class SemesterCreate(Resource):
    @api.doc("create_semester")
    @api.expect(semester_create_model)
    @jwt_required
    def post(self):
        '''Create a new semester'''
        body = request.json
        try:
            semester_id = reporting_service.create_semester(body)
            return {"semester_id": semester_id}
        except Exception as e:
            return {
                'error': "Error creating semester: " + str(e)
            }