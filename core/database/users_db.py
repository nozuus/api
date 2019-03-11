from core.database.db import dynamodb,usersTable,usersIndex
from dynamodb_json import json_util as db_json
import json


def get_user_by_id(user_id):
    query_values = {
        ":user_id": {"S": user_id}
    }

    response = dynamodb.query(TableName=usersTable,
                              KeyConditionExpression="user_id = :user_id",
                              ExpressionAttributeValues=query_values)

    result = db_json.loads(response)["Items"]

    if len(result) > 0:
        return result[0]
    return None


def get_user_by_email(user_email):
    query_values = {
        ":primary_email_address": {"S": user_email}
    }

    response = dynamodb.query(TableName=usersTable,
                              IndexName=usersIndex,
                              KeyConditionExpression="primary_email_address = :primary_email_address",
                              ExpressionAttributeValues=query_values)

    result = db_json.loads(response)["Items"]

    if len(result) > 0:
        return result[0]
    return None


def get_all_users():
    response = dynamodb.scan(TableName=usersTable,
                             Select="ALL_ATTRIBUTES")

    result = db_json.loads(response)["Items"]

    return result


def create_user(user):
    item = json.loads(db_json.dumps(user))

    response = dynamodb.put_item(TableName=usersTable,
                                 Item=item,
                                 ConditionExpression="attribute_not_exists(user_id)")

    return response["ResponseMetadata"]["HTTPStatusCode"] == 200


def update_user(user):
    item = json.loads(db_json.dumps(user))

    response = dynamodb.put_item(TableName=usersTable,
                                 Item=item)

    return response["ResponseMetadata"]["HTTPStatusCode"] == 200