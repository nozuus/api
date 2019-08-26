import core.database.reporting_db as reporting_db
import uuid


def create_report(report_obj):
    report_id = "report_%s" % str(uuid.uuid4())[:8]
    report_obj["pk"] = report_id
    report_obj["sk"] = "report"
    semester = reporting_db.get_item(report_obj["semester_id"], "semester")
    type = reporting_db.get_item(report_obj["report_type_id"], "report_type")
    if semester is None or len(semester) == 0:
        raise Exception("Invalid semester ID")
    if type is None or len(type) == 0:
        raise Exception("Invalid report type ID")
    for role in report_obj["applicable_roles"]:
        role = reporting_db.get_item(role, "role")
        if role is None or len(role) == 0:
            raise Exception("Invalid role ID")
    if reporting_db.put_item_unique_pk(report_obj):
        return str(report_id)
    else:
        raise Exception("Failed to create report")


def create_report_type(report_type_obj):
    type_id = "report_type_%s" % str(uuid.uuid4())[:8]
    report_type_obj["pk"] = type_id
    report_type_obj["sk"] = "report_type"
    if reporting_db.put_item_unique_pk(report_type_obj):
        return str(type_id)
    else:
        raise Exception("Failed to create report type")


def create_semester(semester_obj):
    semester_id = "semester_%s" % str(uuid.uuid4())[:8]
    semester_obj["pk"] = semester_id
    semester_obj["sk"] = "semester"
    if reporting_db.put_item_unique_pk(semester_obj):
        return str(semester_id)
    else:
        raise Exception("Failed to create semester")