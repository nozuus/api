from flask import request
from flask_restplus import Namespace, Resource
from flask_jwt_extended import jwt_required
from api.models.reporting_model import report_create_model, get_report_model, \
    type_create_model, status_model, get_type_model, semester_create_model, get_semester_model, \
    entry_model, full_report_details, add_description, report_form_model, \
    description_question_model, report_form_submission, report_update_model, \
    get_entry_model, set_status_model
from api.models.users_model import get_users_model
import core.services.reporting_service as reporting_service
import core.services.auth_services as auth_services
import core.database.reporting_db as reporting_db
from api.permissions_decorator import check_permissions
import csv
from werkzeug.wrappers import Response
from io import StringIO
import flask_excel as excel
from werkzeug.datastructures import FileStorage

api = Namespace('reporting', description='Reporting related operations')

api.models[report_create_model.name] = report_create_model
api.models[get_report_model.name] = get_report_model
api.models[type_create_model.name] = type_create_model
api.models[get_type_model.name] = get_type_model
api.models[semester_create_model.name] = semester_create_model
api.models[get_semester_model.name] = get_semester_model
api.models[entry_model.name] = entry_model
api.models[full_report_details.name] = full_report_details
api.models[add_description.name] = add_description
api.models[get_users_model.name] = get_users_model
api.models[report_form_model.name] = report_form_model
api.models[description_question_model.name] = description_question_model
api.models[report_form_submission.name] = report_form_submission
api.models[status_model.name] = status_model
api.models[report_update_model.name] = report_update_model
api.models[get_entry_model.name] = get_entry_model
api.models[set_status_model.name] = set_status_model


# Used for bulk upload
upload_parser = api.parser()
upload_parser.add_argument('file', location='files',
                           type=FileStorage, required=True)


@api.route("/create")
class ReportCreate(Resource):
    @api.doc("create_report")
    @api.expect(report_create_model)
    @jwt_required
    @check_permissions("can_manage_reporting", "can_create_reports")
    def post(self):
        '''Create a new report'''
        body = request.json
        report_id = reporting_service.create_report(body)
        return {"report_id": report_id}


@api.route("/")
class ReportList(Resource):
    @api.doc('get_all_reports')
    @api.marshal_list_with(get_report_model)
    @jwt_required
    def get(self):
        '''Fetch all reports'''
        reports = reporting_service.get_reports()
        return reports


@api.route("/adminReports")
class AdminReportList(Resource):
    @api.doc('get_admin_reports')
    @api.marshal_list_with(get_report_model)
    @jwt_required
    def get(self):
        '''Fetch all reports'''
        reports = reporting_service.get_reports(True)
        return reports


@api.route("/<report_id>")
class Report(Resource):
    @api.doc('get_report_by_id')
    @api.marshal_list_with(full_report_details)
    @jwt_required
    def get(self,report_id):
        '''Fetch report by id'''
        try:
            report = reporting_service.get_report_with_details(report_id)
            return report
        except Exception as e:
            return {
                'error': "Error getting report by id: " + str(e)
            }

    @api.doc("update_report_by_id")
    @api.expect(report_update_model)
    @jwt_required
    def put(self, report_id):
        body = request.json
        reporting_service.update_report(report_id, body)
        return { "error": "Success" }


@api.route("/<report_id>/form")
class ReportForm(Resource):
    @api.doc('get_report_form')
    @api.marshal_with(report_form_model)
    @jwt_required
    def get(self, report_id):
        '''Get report form'''
        form = reporting_service.get_report_form(report_id)
        return form

    @api.doc('create_report_form')
    @jwt_required
    @api.expect(report_form_model)
    def post(self, report_id):
        '''Create report form'''
        report_form = request.json
        reporting_service.create_report_form(report_id, report_form)
        return {
            'error': "Success"
        }

    @api.doc("delete_report_form")
    @jwt_required
    def delete(self, report_id):
        reporting_service.delete_report_form(report_id)
        return {"error": "Success"}


@api.route("/<report_id>/form/submit")
class ReportFormSubmit(Resource):
    @api.doc("submit_report_form")
    @api.expect(report_form_submission)
    @jwt_required
    def post(self, report_id):
        '''Submit report form'''
        submission = request.json
        reporting_service.submit_report_form(report_id, submission)
        return {
            "error": "Success"
        }


@api.route("/export/<report_id>")
class Report(Resource):
    @api.doc('export_report_by_id')
    # @api.marshal_list_with(full_report_details)
    @jwt_required
    def get(self,report_id):
        '''Export attendance report (report_type='optionselect') entries into CSV by report id'''
        try:
            report_name, columns, rows = reporting_service.generate_attendance_report_data_by_id(report_id)

            # Inspired by: https://stackoverflow.com/questions/28011341/create-and-download-a-csv-file-from-a-flask-view
            def generate():
                csv_data = StringIO()
                w = csv.DictWriter(csv_data, fieldnames=columns)

                # write header
                w.writeheader()
                yield csv_data.getvalue()
                csv_data.seek(0)
                csv_data.truncate(0)

                # write each line item
                for row in rows.values():
                    w.writerow(row)
                    yield csv_data.getvalue()
                    csv_data.seek(0)
                    csv_data.truncate(0)

            # stream the response as the data is generated
            response = Response(generate(), mimetype='text/csv')
            # add a filename

            filename = report_name.replace(" ", "_").replace("/", "_") + "_Export.csv"
            response.headers.set("Content-Disposition", "attachment", filename=filename)
            return response

        except Exception as e:
            return {
                'error': "Error exporting to CSV for report with id: " + str(e)
            }


@api.route("/<report_id>/checkPermissions")
class Report(Resource):
    @api.doc('check_permissions_for_report')
    @jwt_required
    def get(self,report_id):
        '''Determines whether or not the current user can access the given report'''
        return {
            "can_manage": reporting_service.check_report_permissions(report_id)
        }


@api.route("/<report_id>/applicableUsers")
class Report(Resource):
    @api.doc('get_users_for_report')
    @api.marshal_list_with(get_users_model)
    @jwt_required
    def get(self,report_id):
        '''Get all users that the given report applies to'''
        users = reporting_service.get_applicable_users(report_id)
        return users


@api.route("/<report_id>/presetDescription")
class ReportDescription(Resource):
    @api.doc("create_preset_description")
    @api.expect(add_description)
    @jwt_required
    def post(self, report_id):
        '''Adds a new description to the list of preset descriptions for the report. Used primarily by attendance'''
        body = request.json
        success = reporting_service.add_preset_description(report_id, body["description"])
        return {"error":"Success" if success else "Error"}





@api.route("/<report_id>/entries")
class ReportEntries(Resource):
    @api.doc("create_entry")
    @api.expect(entry_model)
    @jwt_required
    def post(self, report_id):
        '''Add entry to a report'''
        body = request.json
        try:
            existing = request.args.get("checkExisting", default=False, type=bool)
            success = reporting_service.create_report_entry(report_id, body, existing)
            return {"error":"Success" if success else "Error"}
        except Exception as e:
            return {
                'error': "Error creating report entry: " + str(e)
            }

    @api.doc("get_entries")
    @api.marshal_list_with(get_entry_model)
    @jwt_required
    def get(self, report_id):
        try:
            entries = reporting_service.get_report_entries(report_id)
            return entries
        except Exception as e:
            return {
                'error': "Error fetching report entries: " + str(e)
            }


@api.route("/<report_id>/entries/bulkUpload")
class ReportBulkUpload(Resource):
    @api.doc("bulk_upload_entries")
    def get(self, report_id):
        pyexcel_book = reporting_service.get_bulk_upload_sheet(report_id)
        return excel.make_response(pyexcel_book,'xlsx')

    @api.doc("bulk_upload_entrie_submit")
    @api.expect(upload_parser)
    def post(self, report_id):
        args = upload_parser.parse_args()
        uploaded_file = args['file']
        reporting_service.upload_bulk_entries(report_id, uploaded_file)
        return {"error": "Success"}



@api.route("/<report_id>/entries/<user_email>")
class ReportEntriesByUser(Resource):
    @api.doc("get_entries_for_user")
    @api.marshal_list_with(get_entry_model)
    @jwt_required
    def get(self, report_id, user_email):
        username = auth_services.get_identity()
        entries = reporting_service.get_report_entries_for_user(report_id, user_email, username != user_email)
        return entries


@api.route("/<report_id>/entries/<user_email>/<entry_id>")
class DeleteEntry(Resource):
    @api.doc("delete_report_entry")
    @jwt_required
    def delete(self, report_id, user_email, entry_id):
        reporting_service.delete_entry(report_id, user_email, entry_id)
        return {"error": "Success"}


@api.route("/<report_id>/entries/<user_email>/<entry_id>/status")
class StatusUpdate(Resource):
    @api.doc("update_entry_status")
    @api.expect(set_status_model)
    @jwt_required
    def put(self, report_id, user_email, entry_id):
        body = request.json
        reporting_service.update_entry_status(report_id, user_email, entry_id, body["new_status"])
        return {"error": "Success"}


@api.route("/types/create")
class TypeCreate(Resource):
    @api.doc("create_report_type")
    @api.expect(type_create_model)
    @jwt_required
    @check_permissions("can_manage_reporting")
    def post(self):
        '''Create a new report type'''
        body = request.json
        if body["value_type"] == "optionselect" and "options" not in body:
            return {"error": "Value type 'optionselect' requires a list of options"}
        report_type_id = reporting_service.create_report_type(body)
        return {"report_type_id": report_type_id}


@api.route("/types/")
class ReportTypeList(Resource):
    @api.doc('get_all_report_types')
    @api.marshal_list_with(get_type_model)
    @jwt_required
    def get(self):
        '''Fetch all report types'''
        try:
            report_types = reporting_db.get_items_by_type("report_type")
            return report_types
        except Exception as e:
            return {
                'error': "Error getting all report types: " + str(e)
            }


@api.route("/types/<report_type_id>")
class ReportTypeList(Resource):
    @api.doc('get_report_type_by_id')
    @api.marshal_with(get_type_model)
    @jwt_required
    def get(self, report_type_id):
        '''Fetch report type by ID'''
        try:
            report_type = reporting_db.get_item(report_type_id, "report_type")
            if report_type is None:
                raise Exception("Invalid report type id")
            return report_type
        except Exception as e:
            return {
                'error': "Error getting all report types: " + str(e)
            }

    @api.doc('update_report_type')
    @api.expect(type_create_model)
    @jwt_required
    @check_permissions("can_manage_reporting")
    def put(self, report_type_id):
        body = request.json
        reporting_service.update_report_type(report_type_id, body)
        return {
            "error": "Success"
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


@api.route("/semesters/<semester_id>")
class Semester(Resource):
    @api.doc("update_semester")
    @api.expect(semester_create_model)
    @jwt_required
    @check_permissions("can_manage_reporting")
    def put(self, semester_id):
        body = request.json
        reporting_service.update_semester(semester_id, body)
        return {
            "error": "Success"
        }

    @api.doc("get_semester")
    @api.marshal_with(get_semester_model)
    @jwt_required
    def get(self, semester_id):
        semester = reporting_service.get_semester(semester_id)
        return semester


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
