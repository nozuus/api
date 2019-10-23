import boto3
import os
import core.database.users_db as users_db

stage = os.environ.get("stage")

if not stage:
    stage = "dev"

ses = None
if stage == "dev":
    key = os.environ.get("aws_key")
    secret = os.environ.get("aws_secret")
    ses = boto3.client("ses", aws_access_key_id=key, aws_secret_access_key=secret, region_name='us-east-1')
else:
    ses = boto3.client('ses')


def send_plain_email(subject, body, to_emails):
    response = ses.send_email(
        Source= "Otter Pond <mailer@email.theotterpond.com>",
        Destination={
            "ToAddresses": to_emails
        },
        Message={
            'Subject': {
                'Data': subject
            },
            'Body': {
                "Text": {
                    'Data': body
                }
            }
        },
    )
    return response["ResponseMetadata"]["HTTPStatusCode"] == 200


def send_html_body(subject, body, to_emails):
    response = ses.send_email(
        Source="Otter Pond <mailer@email.theotterpond.com>",
        Destination={
            "ToAddresses": to_emails
        },
        Message={
            'Subject': {
                'Data': subject
            },
            'Body': {
                "Html": {
                    'Data': body
                }
            }
        },
    )
    return response["ResponseMetadata"]["HTTPStatusCode"] == 200


def send_verification_email(email_address):
    response = ses.send_custom_verification_email(
        EmailAddress=email_address,
        TemplateName='OtterPondTemplate_' + stage
    )

    return response["ResponseMetadata"]["HTTPStatusCode"] == 200


def verify_email_address(email_address):
    user = users_db.get_user_by_email(email_address)
    if user is None:
        all_users = users_db.get_all_users()
        for cur_user in all_users:
            if email_address in cur_user["other_emails"]:
                user = cur_user
                break
        if user is None:
            raise Exception("Invalid user email")
    response = boto3.client('ses').get_identity_verification_attributes(
        Identities=[email_address])
    if len(response["VerificationAttributes"]) > 0:
        verification_status = response["VerificationAttributes"][email_address]
        if verification_status == "Success":
            raise Exception("Email Address Already Verified")

    return send_verification_email(email_address)