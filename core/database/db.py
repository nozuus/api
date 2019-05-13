import boto3
import os

table = "OtterPondTable"
reverseIndex = "OtterPondTable-Reverse"

dynamodb = None
if os.environ.get("stage") == "dev":
    key = os.environ.get("aws_key")
    secret = os.environ.get("aws_secret")
    dynamodb = boto3.client("dynamodb", aws_access_key_id=key, aws_secret_access_key=secret, region_name='us-east-1')
else:
    dynamodb = boto3.client('dynamodb')