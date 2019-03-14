from core.database.db import dynamodb,rolesTable
from dynamodb_json import json_util as db_json
import json


def get_role_by_id(role_id):
    query_values = {
        ":role_id": {"S": role_id}
    }

    response = dynamodb.query(TableName=rolesTable,
                              KeyConditionExpression="role_id = :role_id",
                              ExpressionAttributeValues=query_values)

    result = db_json.loads(response)["Items"]

    if len(result) > 0:
        return result[0]
    return None


def get_all_roles():
    response = dynamodb.scan(TableName=rolesTable,
                             Select="ALL_ATTRIBUTES")

    result = db_json.loads(response)["Items"]

    return result


def create_role(role):
    item = json.loads(db_json.dumps(role))

    response = dynamodb.put_item(TableName=rolesTable,
                                 Item=item,
                                 ConditionExpression="attribute_not_exists(role_id)")

    return response["ResponseMetadata"]["HTTPStatusCode"] == 200


def delete_role(role):
    item = json.loads(db_json.dumps(role))

    response = dynamodb.delete_item(TableName=rolesTable,
                                    Key=item)

    return response["ResponseMetadata"]["HTTPStatusCode"] == 200
