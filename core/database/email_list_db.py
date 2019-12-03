from core.database.db import dynamodb, table, reverseIndex, put_item_no_check, delete_item, get_items_by_type, get_item
from dynamodb_json import json_util as db_json
import json


def get_email_list_by_address(address):
    query_values = {
        ":address": {"S": address},
        ":type": {"S": "list"}
    }

    response = dynamodb.query(TableName=table,
                              KeyConditionExpression="pk = :address AND sk = :type",
                              ExpressionAttributeValues=query_values)

    result = db_json.loads(response)["Items"]

    if len(result) > 0:
        return result[0]
    return None


def get_users_on_list(list_address):
    query_values = {
        ":list_address": {"S": "list_%s" % list_address}
    }

    response = dynamodb.query(TableName=table,
                              IndexName=reverseIndex,
                              KeyConditionExpression="sk = :list_address",
                              ExpressionAttributeValues=query_values)
    return db_json.loads(response)["Items"]


def get_user_subscriptions(user_email):
    query_values = {
        ":key": {"S": user_email},
        ":type": {"S": "list_"}
    }

    response = dynamodb.query(TableName=table,
                              KeyConditionExpression="pk = :key AND begins_with(sk,:type)",
                              ExpressionAttributeValues=query_values)
    return db_json.loads(response)["Items"]


"""Edit subscriptions list"""


def add_to_list(address, user_email):
    subscription = {
        "pk": user_email,
        "sk": "list_%s" % address
    }
    item = json.loads(db_json.dumps(subscription))
    response = dynamodb.put_item(TableName=table,
                                 Item=item)

    return response["ResponseMetadata"]["HTTPStatusCode"] == 200


def get_all_email_lists():
    query_values = {
        ":type": {"S": "list"}
    }

    response = dynamodb.query(TableName=table,
                              IndexName=reverseIndex,
                              KeyConditionExpression="sk = :type",
                              ExpressionAttributeValues=query_values)

    result = db_json.loads(response)["Items"]

    return result


def create_email_list(email_list):
    item = json.loads(db_json.dumps(email_list))

    response = dynamodb.put_item(TableName=table,
                                 Item=item,
                                 ConditionExpression="attribute_not_exists(pk)")

    return response["ResponseMetadata"]["HTTPStatusCode"] == 200


def save_role_permissions(permission):
    item = json.loads(db_json.dumps(permission))

    response = dynamodb.put_item(TableName=table,
                                 Item=item)

    return response["ResponseMetadata"]["HTTPStatusCode"] == 200


def get_role_permissions(address):
    query_values = {
        ":address": {"S": address},
        ":type": {"S": "list_permission"}
    }

    response = dynamodb.query(TableName=table,
                              KeyConditionExpression="pk = :address AND begins_with(sk,:type)",
                              ExpressionAttributeValues=query_values)

    result = db_json.loads(response)["Items"]

    return result


def get_role_permissions_by_role(address, role_id):
    query_values = {
        ":address": {"S": address},
        ":type": {"S": "list_permission_%s" % role_id}
    }

    response = dynamodb.query(TableName=table,
                              KeyConditionExpression="pk = :address AND sk = :type",
                              ExpressionAttributeValues=query_values)

    result = db_json.loads(response)["Items"]

    if len(result) > 0:
        return result[0]

    return None


def get_all_role_permissions_by_role(role_id):
    query_values = {
        ":key": {"S": "list_permission_%s" % role_id}
    }

    response = dynamodb.query(TableName=table,
                              IndexName=reverseIndex,
                              KeyConditionExpression = "sk = :key",
                              ExpressionAttributeValues = query_values)

    return db_json.loads(response)["Items"]


def store_message_id(message_id, timestamp):
    to_store = {
        "pk": "message_id_cache",
        "sk": message_id,
        "timestamp": timestamp
    }

    item = json.loads(db_json.dumps(to_store))

    response = dynamodb.put_item(TableName=table,
                                 Item=item)

    return response["ResponseMetadata"]["HTTPStatusCode"] == 200


def check_message_id(message_id):
    query_values = {
        ":pkey" : {"S": "message_id_cache"},
        ":message_id": {"S": message_id}
    }

    response = dynamodb.query(TableName=table,
                              KeyConditionExpression="pk = :pkey AND sk = :message_id",
                              ExpressionAttributeValues=query_values)

    if len(db_json.loads(response)["Items"]) > 0:
        return True
    return False
