import boto3
import os

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