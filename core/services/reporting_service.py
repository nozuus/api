import core.database.reporting_db as reporting_db
import core.database.users_db as users_db
import core.database.roles_db as roles_db
import core.services.config_service as config_service
import core.services.users_service as users_service
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


def create_report_entry(report_id, entry, existing = False):
    report = reporting_db.get_item(report_id, "report")
    if report is None:
        raise Exception("Invalid report ID")

    if "user_email" not in entry or entry["user_email"] is None:
        if "gtid" not in entry or entry["gtid"] is None:
            raise Exception("Either user_email or gtid is required")
        user_email = users_service.get_user_by_gtid(entry["gtid"])
        if user_email is None:
            raise Exception("Invalid gtid")
        entry["user_email"] = user_email
        del entry["gtid"]
    else:
        user = reporting_db.get_item(entry["user_email"], "user")
        if user is None:
            raise Exception("Invalid user email")

    entry_id = "entry_%s_%s" % (entry["user_email"], str(uuid.uuid4())[:4])
    entry["pk"] = report_id
    entry["sk"] = entry_id
    report_type = reporting_db.get_item(report["report_type_id"], "report_type")

    if (report_type["value_type"] == "numeric" or report_type["value_type"] == "financial") and not is_number(entry["value"]):
        raise Exception("Invalid report value type")
    if report_type["value_type"] == "optionselect" and entry["value"] not in report_type["options"]:
        raise Exception("Invalid report value option")

    permissions = report_type["management_permissions"]

    if not config_service.check_permissions(permissions):
        raise Exception("User does not have permissions to add report entry")

    if existing == True:
        if len(reporting_db.checkReportEntryForUser(report_id, entry["user_email"], entry["description"])) > 0:
            raise Exception("Entry already exists for user")

    if reporting_db.put_item_unique_pk(entry):
        return True
    else:
        raise Exception("Failed to create report entry");


def get_report_entries(report_id):
    if not check_report_permissions(report_id):
        raise Exception("User does not have permissions to access this report")
    report = reporting_db.get_item(report_id, "report")

    if report is None:
        raise Exception("Invalid Report ID")

    report_type = reporting_db.get_item(report["report_type_id"], "report_type")

    permissions = report_type["management_permissions"]

    if not config_service.check_permissions(permissions):
        raise Exception("User does not have permissions to view report entries")

    return reporting_db.get_report_entries(report_id)


def get_report_entries_for_user(report_id, user_email, check_permissions):
    if check_permissions and not check_report_permissions(report_id):
        raise Exception("User does not have permissions to access this report")

    entries = reporting_db.get_report_entries_for_user(report_id, user_email)
    return entries


def check_report_permissions(report_id):
    report = reporting_db.get_item(report_id, "report")
    if report is None:
        raise Exception("Invalid report id")
    report_type = reporting_db.get_item(report["report_type_id"], "report_type")
    report_permissions = report_type["management_permissions"]
    report_permissions.append("can_manage_reporting")
    return config_service.check_permissions(report_permissions)


def get_applicable_users(report_id):
    report = reporting_db.get_item(report_id, "report")
    if report is None:
        raise Exception("Invalid report id")
    all_users = users_db.get_all_users()
    if len(all_users) == 0:
        raise Exception("Unable to fetch all users")

    applicable_users = []
    for role in report["applicable_roles"]:
        user_roles = roles_db.get_users_by_role(role)
        applicable_users = applicable_users + [user_role["pk"] for user_role in user_roles]

    return [user for user in all_users if user["pk"] in applicable_users]


def get_report_with_details(report_id):
    report = reporting_db.get_item(report_id, "report")
    report["report_type"] = reporting_db.get_item(report["report_type_id"], "report_type")
    report["semester"] = reporting_db.get_item(report["semester_id"], "semester")
    return report;


def add_preset_description(report_id, description):
    report = reporting_db.get_item(report_id, "report")
    if report is None:
        raise Exception("Invalid report id")

    descriptions = []
    if "preset_descriptions" in report:
        descriptions = report["preset_descriptions"]

    descriptions.append(description)

    report["preset_descriptions"] = descriptions

    return reporting_db.put_item_no_check(report)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False