from flask import request
from flask_restplus import Namespace, Resource
from flask_jwt_extended import jwt_required
from api.models.reporting_model import report_create_model, get_report_model, type_create_model, get_type_model, semester_create_model, get_semester_model, entry_model
import core.services.reporting_service as reporting_service
import core.database.reporting_db as reporting_db
from api.permissions_decorator import check_permissions

api = Namespace('reporting', description='Reporting related operations')

api.models[report_create_model.name] = report_create_model
api.models[get_report_model.name] = get_report_model
api.models[type_create_model.name] = type_create_model
api.models[get_type_model.name] = get_type_model
api.models[semester_create_model.name] = semester_create_model
api.models[get_semester_model.name] = get_semester_model
api.models[entry_model.name] = entry_model


@api.route("/create")
class ReportCreate(Resource):
    @api.doc("create_report")
    @api.expect(report_create_model)
    @jwt_required
    @check_permissions("can_manage_reporting", "can_create_reports")
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


@api.route("/")
class ReportList(Resource):
    @api.doc('get_all_reports')
    @api.marshal_list_with(get_report_model)
    @jwt_required
    def get(self):
        '''Fetch all reports'''
        try:
            reports = reporting_db.get_items_by_type("report")
            return reports
        except Exception as e:
            return {
                'error': "Error getting all reports: " + str(e)
            }


@api.route("/<report_id>/entries")
class ReportEntries(Resource):
    @api.doc("create_entry")
    @api.expect(entry_model)
    @jwt_required
    @check_permissions("can_manage_reporting")
    def post(self, report_id):
        '''Add entry to a report'''
        body = request.json
        try:
            success = reporting_service.create_report_entry(report_id, body)
            return {"error":"Success" if success else "Error"}
        except Exception as e:
            return {
                'error': "Error creating report entry: " + str(e)
            }

    @api.doc("get_entries")
    @api.marshal_list_with(entry_model)
    @jwt_required
    def get(self, report_id):
        try:
            entries = reporting_db.get_report_entries(report_id)
            return entries
        except Exception as e:
            return {
                'error': "Error fetching report entries: " + str(e)
            }


@api.route("/<report_id>/entries/<user_email>")
class ReportEntriesByUser(Resource):
    @api.doc("get_entries_for_user")
    @api.marshal_list_with(entry_model)
    @jwt_required
    def get(self, report_id, user_email):
        try:
            entries = reporting_db.get_report_entries_for_user(report_id, user_email)
            return entries
        except Exception as e:
            return {
                'error': "Error fetching report entries: " + str(e)
            }


@api.route("/types/create")
class TypeCreate(Resource):
    @api.doc("create_report_type")
    @api.expect(type_create_model)
    @jwt_required
    @check_permissions("can_manage_reporting")
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


@api.route("/types/")
class ReportTypeList(Resource):
    @api.doc('get_all_report_types')
    @api.marshal_list_with(get_type_model)
    @jwt_required
    def get(self):
        '''Fetch all reports'''
        try:
            report_types = reporting_db.get_items_by_type("report_type")
            return report_types
        except Exception as e:
            return {
                'error': "Error getting all report types: " + str(e)
            }


@api.route("/semesters/create")
class SemesterCreate(Resource):
    @api.doc("create_semester")
    @api.expect(semester_create_model)
    @jwt_required
    @check_permissions("can_manage_reporting")
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


@api.route("/semesters/")
class SemestersList(Resource):
    @api.doc('get_all_semesters')
    @api.marshal_list_with(get_semester_model)
    @jwt_required
    def get(self):
        '''Fetch all reports'''
        try:
            semesters = reporting_db.get_items_by_type("semester")
            return semesters
        except Exception as e:
            return {
                'error': "Error getting all semesters: " + str(e)
            }
