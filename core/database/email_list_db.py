from core.database.db import dynamodb, subscriptionsTable, emailTable
from core.database.db import emailIndex, usersTable, subscriptionsIndex
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


def get_email_list_by_id(list_id):
    query_values = {
        ":list_id": {"S": list_id}
    }

    response = dynamodb.query(TableName=emailTable,
                              KeyConditionExpression="list_id = :list_id",
                              ExpressionAttributeValues=query_values)

    result = db_json.loads(response)["Items"]

    if len(result) > 0:
        return result[0]
    return None


def get_users_on_list(list_id):
    query_values = {
        ":list_id": {"S": list_id}
    }

    response = dynamodb.query(TableName=subscriptionsTable,
                              KeyConditionExpression="list_id = :list_id",
                              ExpressionAttributeValues=query_values)
    return db_json.loads(response)["Items"]


"""Edit subscriptions list"""


def add_to_list(subscription):
    item = json.loads(db_json.dumps(subscription))
    response = dynamodb.put_item(TableName=subscriptionsTable,
                                 Item=item)

    return response["ResponseMetadata"]["HTTPStatusCode"] == 200


def update_user_email(user_id, new_email):
    subscriptions = get_subscriptions_by_user(user_id)

    # Batch write can handle chunks of 25 requests, so lets do 20 to play it
    # safe
    subscription_chunks = divide_chunks(subscriptions, 20)

    for chunk in subscription_chunks:
        items = []
        for subscription in chunk:
            subscription["user_primary_email_address"] = new_email
            item = {
                "PutRequest": {
                    "Item": json.loads(db_json.dumps(subscription))
                }
            }
            items.append(item)

        request_item = {
            subscriptionsTable: items
        }
        response = dynamodb.batch_write_item(RequestItems=request_item)

        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            return 0
    return 1


def get_subscriptions_by_user(user_id):
    query_values = {
        ":user_id": {"S": user_id}
    }

    response = dynamodb.query(TableName=subscriptionsTable,
                              IndexName=subscriptionsIndex,
                              KeyConditionExpression="user_id = :user_id",
                              ExpressionAttributeValues=query_values)

    return db_json.loads(response)["Items"]


def get_all_email_lists():
    response = dynamodb.scan(TableName=emailTable,
                             Select="ALL_ATTRIBUTES")

    result = db_json.loads(response)["Items"]

    return result



# TODO: Move to utils file
def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]