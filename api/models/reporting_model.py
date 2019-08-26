from flask_restplus import fields, Model

report_create_model = Model("ReportCreate", {
    'name': fields.String,
    'description': fields.String,
    'report_type_id': fields.String,
    'semester_id': fields.String,
    'applicable_roles': fields.List(fields.String),
})

get_report_model = Model.inherit("GetReports", report_create_model, {
    "report_id": fields.String(attribute='pk')
})

type_create_model = Model("ReportTypeCreate", {
    'name': fields.String,
    'management_permissions': fields.List(fields.String),
    'value_type': fields.String(enum=['numeric', 'financial', 'optionselect']),
    'options': fields.List(fields.String, description="Possible options for optionselect value type", default=None)
})

get_type_model = Model.inherit("GetReportTypes", type_create_model, {
    "report_type_id": fields.String(attribute='pk')
})

semester_create_model = Model("SemesterCreate", {
    'start_date': fields.Date,
    'end_date': fields.Date,
    'description': fields.String
})

get_semester_model = Model.inherit("GetSemesters", type_create_model, {
    "semester_id": fields.String(attribute='pk')
})