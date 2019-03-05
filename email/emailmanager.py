import boto3
import json

def email_received(event, context):
    record = event["Records"][0]
    message = json.loads(record["Sns"]["Message"])

    if message["notificationType"] == "Received":
        mail = message["mail"]
        from_email = mail["source"]
        message_id = mail["messageId"]
        to_emails = mail["destination"]

        print("From email: ", from_email)
        print("Message ID: ", message_id)
        print("To Emails: ", to_emails)
    else:
        print("Message not received. Terminating")
