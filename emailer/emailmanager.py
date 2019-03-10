import json
import core.services.emailer_service as emailer_service


def email_received(event, context):
    record = event["Records"][0]
    message = json.loads(record["Sns"]["Message"])

    if message["notificationType"] == "Received":
        mail = message["mail"]
        emailer_service.process_received_email(mail)

    else:
        print("Message not received. Terminating")
