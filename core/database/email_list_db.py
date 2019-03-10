from core.database.db import dynamodb, subscriptionsTable, emailTable, emailIndex, usersTable
from dynamodb_json import json_util as db_json
import json


def get_email_list(prefix, domain):
    query_values = {
        ":domain": {"S": domain},
        ":prefix": {"S": prefix}
    }
    response = dynamodb.query(TableName=emailTable,
                              IndexName=emailIndex,
                              KeyConditionExpression="#d = :domain AND prefix = :prefix",
                              ExpressionAttributeNames={"#d" : "domain"},
                              ExpressionAttributeValues=query_values)

    result = db_json.loads(response)["Items"]
    if len(result) > 0:
        return result[0]
    return


def get_users_on_list(list_id):
    query_values = {
        ":list_id": {"S": list_id}
    }

    response = dynamodb.query(TableName=subscriptionsTable,
                              KeyConditionExpression="list_id = :list_id",
                              ExpressionAttributeValues=query_values)
    return db_json.loads(response)["Items"]


"""Edit subscriptions list"""


def add_to_list(user_id, list_id):
    preItem = {
        "user_id": user_id,
        "list_id": list_id
    }
    item = json.loads(db_json.dumps(preItem))
    response = dynamodb.put_item(TableName=subscriptionsTable,
                                 Item=item)

    return response["ResponseMetadata"]["HTTPStatusCode"] == 200
