from core.database.db import dynamodb, table, reverseIndex, delete_item
from dynamodb_json import json_util as db_json
import json


def get_role_by_id(role_id):
    query_values = {
        ":role_id": {"S": role_id},
        ":type": {"S": "role"}
    }

    response = dynamodb.query(TableName=table,
                              KeyConditionExpression="pk = :role_id AND sk = :type",
                              ExpressionAttributeValues=query_values)

    result = db_json.loads(response)["Items"]

    if len(result) > 0:
        return result[0]
    return None


def get_all_roles():
    query_values = {
        ":type": {"S": "role"}
    }

    response = dynamodb.query(TableName=table,
                              IndexName=reverseIndex,
                              KeyConditionExpression="sk = :type",
                              ExpressionAttributeValues=query_values)

    result = db_json.loads(response)["Items"]

    return result


def create_role(role):
    item = json.loads(db_json.dumps(role))

    response = dynamodb.put_item(TableName=table,
                                 Item=item,
                                 ConditionExpression="attribute_not_exists(pk)")

    return response["ResponseMetadata"]["HTTPStatusCode"] == 200


def update_role(user):
    item = json.loads(db_json.dumps(user))

    response = dynamodb.put_item(TableName=table,
                                 Item=item)

    return response["ResponseMetadata"]["HTTPStatusCode"] == 200


def set_user_role(user_email, role_id):
    item = json.loads(db_json.dumps({
        "pk": user_email,
        "sk": role_id
    }))

    response = dynamodb.put_item(TableName=table,
                                 Item=item)

    return response["ResponseMetadata"]["HTTPStatusCode"] == 200


def get_users_by_role(role_id):
    query_values = {
        ":role_id": {"S": role_id}
    }

    response = dynamodb.query(TableName=table,
                              IndexName=reverseIndex,
                              KeyConditionExpression="sk = :role_id",
                              ExpressionAttributeValues=query_values)

    result = db_json.loads(response)["Items"]

    return result


def get_role_by_user(user_email):
    query_values = {
        ":email": {"S": user_email},
        ":role": {"S": "role"},
    }

    response = dynamodb.query(TableName=table,
                              KeyConditionExpression="pk = :email AND begins_with (sk,:role)",
                              ExpressionAttributeValues=query_values)

    result = db_json.loads(response)["Items"]

    if len(result) > 0:
        return result[0]
    return None


