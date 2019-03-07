import boto3
import json
import core.db as db
from botocore.exceptions import ClientError
import email


def email_received(event, context):
    record = event["Records"][0]
    message = json.loads(record["Sns"]["Message"])

    if message["notificationType"] == "Received":
        mail = message["mail"]
        from_email = mail["source"]
        message_id = mail["messageId"]
        to_emails = mail["destination"]

        print("From email: ", from_email)
        print("To Emails: ", to_emails)

        list_ids = []
        for to_email in to_emails:
            split = to_email.split("@")
            prefix = split[0]
            domain = split[1]
            print("Prefix: %s, Domain: %s" %(prefix,domain))
            entries = db.get_email_list(prefix, domain)
            if len(entries) > 0:
                list_ids.append(entries[0]["list_id"])

        print("Trying to read file now")

        s3 = boto3.resource("s3")
        key = "received/" + message_id
        obj = s3.Object("nozuus-emails", key)
        file_contents = obj.get()['Body'].read()
        print("Read content: ", file_contents)

        msg = email.message_from_bytes(file_contents)

        msg_from = msg["From"]
        msg_from_split = msg_from.split("<")
        msg_from_name = msg_from_split[0];
        msg_from_email = msg_from_split[1].split(">")[0]
        del msg['Return-Path']
        del msg['From']
        del msg['Reply-To']
        msg["From"] = "%s <mailer@email.theotterpond.com>" % (msg_from_name)
        from_configured = "%s <%s>" % (msg_from_name, msg_from_email)
        msg["Reply-To"] = from_configured

        print("From: ", msg["From"])
        print("Return-Path: ", msg["Return-Path"])
        print("Source: ", msg["Source"])
        print("Reply-To: ", msg["Reply-To"])
        email_client = boto3.client('ses')

        try:
            # Provide the contents of the email.
            response = email_client.send_raw_email(
                Destinations=[
                    '',
                ],
                RawMessage={
                    'Data': msg.as_string()
                },
            )
        # Display an error if something goes wrong.
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent! Message ID:"),
            print(response['MessageId'])

    else:
        print("Message not received. Terminating")
