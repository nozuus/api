import boto3
import json
from dynamodb_json import json_util as db_json

usersTable = "Users-1"
emailTable = "EmailLists-1"
subscriptionsTable = "Subscriptions-1"

dynamodb = boto3.client('dynamodb')


def get_email_list(prefix, domain):
    query_values = {
        ":domain": {"S": domain},
        ":prefix": {"S": prefix}
    }
    response = dynamodb.query(TableName=emailTable,
                              IndexName="EmailListCombined",
                              KeyConditionExpression="#d = :domain AND prefix = :prefix",
                              ExpressionAttributeNames={"#d" : "domain"},
                              ExpressionAttributeValues=query_values)
    return db_json.loads(response)["Items"]


def get_users_on_list(list_id):
    query_values = {
        ":list_id": {"S": list_id}
    }

    response = dynamodb.query(TableName=subscriptionsTable,
                              KeyConditionExpression="list_id = :list_id",
                              ExpressionAttributeValues=query_values)
    return db_json.loads(response)["Items"]

def get_user_by_id(user_id):
    query_values = {
        ":user_id": {"S": user_id}
    }

    response = dynamodb.query(TableName=usersTable,
                              KeyConditionExpression="user_id = :user_id",
                              ExpressionAttributeValues=query_values)

    return db_json.loads(response)["Items"]