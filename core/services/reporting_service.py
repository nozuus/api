import core.database.reporting_db as reporting_db
import core.services.config_service as config_service
import uuid


def create_report(report_obj):
    report_id = "report_%s" % str(uuid.uuid4())[:8]
    report_obj["pk"] = report_id
    report_obj["sk"] = "report"
    semester = reporting_db.get_item(report_obj["semester_id"], "semester")
    type = reporting_db.get_item(report_obj["report_type_id"], "report_type")
    if semester is None:
        raise Exception("Invalid semester ID")
    if type is None:
        raise Exception("Invalid report type ID")
    for role in report_obj["applicable_roles"]:
        role = reporting_db.get_item(role, "role")
        if role is None:
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


def create_report_entry(report_id, entry):
    entry_id = "entry_%s_%s" % (entry["user_email"], str(uuid.uuid4())[:4])
    entry["pk"] = report_id
    entry["sk"] = entry_id

    report = reporting_db.get_item(report_id, "report")
    user = reporting_db.get_item(entry["user_email"], "user")

    if report is None:
        raise Exception("Invalid report ID")
    if user is None:
        raise Exception("Invalid user email")

    report_type = reporting_db.get_item(report["report_type_id"], "report_type")

    if (report_type["value_type"] == "numeric" or report_type["value_type"] == "financial") and not is_number(entry["value"]):
        raise Exception("Invalid report value type")
    if report_type["value_type"] == "optionselect" and entry["value"] not in report_type["options"]:
        raise Exception("Invalid report value option")

    if reporting_db.put_item_unique_pk(entry):
        return True
    else:
        raise Exception("Failed to create report entry");


def get_report_entries_for_user(report_id, check_permissions):
    if check_permissions:
        report = reporting_db.get_item(report_id, "report")
        report_type = reporting_db.get_item(report["report_type_id"], "report_type")
        if not config_service.check_permissions(report_type["management_permissions"]):
            raise Exception("User does not have permissions to view these entries")

    entries = reporting_db.get_report_entries(report_id)
    return entries


def get_report_with_details(report_id):
    report = reporting_db.get_item(report_id, "report")
    report["report_type"] = reporting_db.get_item(report["report_type_id"], "report_type")
    report["semester"] = reporting_db.get_item(report["semester_id"], "semester")
    return report;

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False