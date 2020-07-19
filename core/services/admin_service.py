import core.services.reporting_service as reporting_service
import core.services.auth_services as auth_service
import core.database.reporting_db as reporting_db
import core.services.users_service as users_service
from functools import reduce
import yaml
import os
from datetime import datetime


def inject_variables(file_string, config):
    file_string = file_string.replace("_semester_", config["semester_description"])
    for variable in config["other_variables"]:
        file_string = file_string.replace("_" + variable + "_", config["other_variables"][variable])

    return file_string


def launch_semester(config):
    with open("resources/semester_launch_template.yml") as template_file:
        template_file_string = template_file.read()
        semester_id = reporting_service.create_semester({
            "start_date": config["semester_start_date"],
            "end_date": config["semester_end_date"],
            "description": config["semester_description"]
        })

        template_file_string = inject_variables(template_file_string, config)
        template = yaml.safe_load(template_file_string)

        stage = os.environ.get("stage")

        if not stage:
            stage = "dev"

        template = template[stage]

        for report_config in template["reports"]:
            report_id = reporting_service.create_report({
                "name": report_config["name"],
                "description": report_config["description"],
                "report_type_id": report_config["report_type_id"],
                "semester_id": semester_id,
                "applicable_roles": report_config["applicable_roles"]
            })
            if report_config["self_reporting_enabled"]:
                reporting_service.create_report_form(report_id, {
                    "valueQuestion": report_config["value_question"],
                    "descriptionQuestions": [
                        {
                            "question": question["question"],
                            "answerType": question["type"]
                        }
                        for question in report_config["description_questions"]
                    ]
                })
            if report_config["rollover_enabled"]:
                rollover_report_id = report_config["rollover_report_id"]
                entries = reporting_service.get_report_entries(rollover_report_id)
                users = users_service.get_all_users()
                roles = report_config["applicable_roles"]

                rollover_report = reporting_db.get_item(rollover_report_id, "report")
                if rollover_report is None:
                    raise Exception("Invalid report ID")

                if rollover_report["report_type_id"] != report_config["report_type_id"]:
                    raise Exception("Rollovers have to have the same report type")

                report_type = reporting_db.get_item(report_config["report_type_id"], "report_type")

                filtered_users = filter(lambda x: x["role_id"] in roles, users)
                for user in filtered_users:
                    user_entries = filter(lambda x: x["user_email"] == user["pk"], entries)
                    total = 0
                    for entry in user_entries:
                        total += entry["value"]

                    if total == 0:
                        continue

                    zero_entry = {
                        "description": "Rollover to " + report_config["name"],
                        "value": -total,
                        "user_email": user["pk"],
                        "entered_by_email": auth_service.get_identity(),
                        "timestamp": datetime.now()
                    }
                    reporting_service.create_report_entry(rollover_report_id, zero_entry, preload_report_type=report_type)

                    rollover_entry = {
                        "description": "Rollover from " + rollover_report["name"],
                        "value": total,
                        "user_email": user["pk"],
                        "entered_by_email": auth_service.get_identity(),
                        "timestamp": datetime.now()
                    }
                    reporting_service.create_report_entry(report_id, rollover_entry, preload_report_type=report_type)
