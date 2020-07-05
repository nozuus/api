import core.services.reporting_service as reporting_service
import yaml
import os


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
