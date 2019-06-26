import boto3
import os

stage = os.environ.get("stage")

if not stage:
    stage = "dev"
table = "OtterPondTable-%s" % stage
reverseIndex = "OtterPondTable-Reverse-%s" % stage

dynamodb = None
if stage == "dev":
    key = os.environ.get("aws_key")
    secret = os.environ.get("aws_secret")
    dynamodb = boto3.client("dynamodb", aws_access_key_id=key, aws_secret_access_key=secret, region_name='us-east-1')
else:
    dynamodb = boto3.client('dynamodb')