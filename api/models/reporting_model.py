from flask_restplus import fields, Model


status_model = Model("StatusOptions", {
    "statuses": fields.List(fields.String),
    "default_status": fields.String(default=None),
    "approved_status": fields.String(default=None)
})

report_create_model = Model("ReportCreate", {
    'name': fields.String,
    'description': fields.String,
    'report_type_id': fields.String,
    'semester_id': fields.String,
    'applicable_roles': fields.List(fields.String),
    'preset_descriptions': fields.List(fields.String, default=None, skip_none=True),
})

report_update_model = Model("ReportUpdate", {
    'name': fields.String,
    'description': fields.String,
    'applicable_roles': fields.List(fields.String),
})

get_report_model = Model.inherit("GetReports", report_create_model, {
    "report_id": fields.String(attribute='pk'),
})

type_create_model = Model("ReportTypeCreate", {
    'name': fields.String,
    'management_permissions': fields.List(fields.String),
    'value_type': fields.String(enum=['numeric', 'financial', 'optionselect']),
    'options': fields.List(fields.String, description="Possible options for optionselect value type", default=None),
    'status_options': fields.Nested(status_model, default=None, skip_none=True)
})

get_type_model = Model.inherit("GetReportTypes", type_create_model, {
    "report_type_id": fields.String(attribute='pk')
})

semester_create_model = Model("SemesterCreate", {
    'start_date': fields.Date,
    'end_date': fields.Date,
    'description': fields.String
})

get_semester_model = Model.inherit("GetSemesters", semester_create_model, {
    "semester_id": fields.String(attribute='pk')
})

entry_model = Model("Entry", {
    'description': fields.String,
    'value': fields.Raw,
    'timestamp': fields.DateTime,
    'user_email': fields.String(),
    'gtid': fields.String(default=None, skip_none=True),
    'entered_by_email': fields.String,
    'status': fields.String(default=None, skip_none=True)
})

get_entry_model = Model.inherit("GetEntry", entry_model, {
    "entry_id": fields.String(attribute='sk')
})

full_report_details = Model.inherit("GetFullReportDetails", get_report_model, {
    "report_type": fields.Nested(get_type_model),
    "semester": fields.Nested(get_semester_model)
})

add_description = Model("AddDescription", {
    'description': fields.String
})

description_question_model = Model("DescriptionQuestion", {
    "question": fields.String,
    "answerType": fields.String
})

report_form_model = Model("ReportForm", {
    'valueQuestion': fields.String,
    'descriptionQuestions': fields.List(fields.Nested(description_question_model))
})

report_form_submission = Model("ReportFormSubmission", {
    'value': fields.Raw,
    'descriptionQuestionAnswers': fields.List(fields.String),
    'timestamp': fields.DateTime,
    'user_email': fields.String(),
    'entered_by_email': fields.String
})

set_status_model = Model("SetStatus", {
    "new_status": fields.String
})