import boto3
import os

usersTable = "Users-1"
usersIndex = "UserByPrimaryEmail-1"
usersSecondaryIndex = "UserBySecondaryEmail-1"
emailTable = "EmailLists-1"
emailIndex = "EmailListCombined-1"
subscriptionsTable = "Subscriptions-1"
subscriptionsIndex = "SubscriptionByUser-1"
rolesTable = "Roles-1"

dynamodb = None
if os.environ.get("stage") == "dev":
    key = os.environ.get("aws_key")
    secret = os.environ.get("aws_secret")
    dynamodb = boto3.client("dynamodb", aws_access_key_id=key, aws_secret_access_key=secret, region_name='us-east-1')
else:
    dynamodb = boto3.client('dynamodb')