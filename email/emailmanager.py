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
            lists = db.get_email_list(prefix, domain)
            if len(lists) > 0:
                list_ids.append(lists[0]["list_id"])

        print("List IDs: ", list_ids)

        user_emails = []
        for list_id in list_ids:
            users_on_list = db.get_users_on_list(list_id)
            print("Subscriptions: ", users_on_list)
            for user_on_list in users_on_list:
                user = db.get_user_by_id(user_on_list["user_id"])
                print("User: ", user)
                user_emails.append(user[0]["primary_email_address"])

        print("User emails: ", user_emails)

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
        safe_from = '%s <mailer@email.theotterpond.com>' % (msg_from_name)
        user_from = "%s <%s>" % (msg_from_name, msg_from_email)
        msg["Reply-To"] = user_from
        msg["From"] = safe_from
        msg["Return-Path"] = "mailer@email.theotterpond.com"
        msg["Source"] = "mailer@email.theotterpond.com"

        print("From: ", msg["From"])
        print("Return-Path: ", msg["Return-Path"])
        print("Source: ", msg["Source"])
        print("Reply-To: ", msg["Reply-To"])
        email_client = boto3.client('ses')

        try:
            # Provide the contents of the email.
            response = email_client.send_raw_email(
                Destinations=user_emails,
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
