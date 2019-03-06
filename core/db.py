import boto3
import json
from dynamodb_json import json_util as db_json

usersTable = "Users-1"
emailTable = "EmailLists-1"
subscriptionsTable = "Subscriptions-1"

dynamodb = boto3.client('dynamodb')


def get_email_list_id(prefix, domain):
    s = domain
    queryValues = {
        ":domain" : {"S": domain},
        ":prefix" : {"S": prefix}
    }
    response = dynamodb.query(TableName=emailTable,
                              IndexName="EmailListCombined",
                              KeyConditionExpression="#d = :domain AND prefix = :prefix",
                              ExpressionAttributeNames={"#d" : "domain"},
                              ExpressionAttributeValues=queryValues)
    return db_json.loads(response)