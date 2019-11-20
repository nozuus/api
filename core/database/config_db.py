from core.database.db import dynamodb, table, get_items_by_type, get_item, put_item_no_check
from dynamodb_json import json_util as db_json
import json

def get_permissions():
    query_values = {
        ":report_id": {"S": "config"},
        ":type": {"S": "permission"}
    }

    response = dynamodb.query(TableName=table,
                              KeyConditionExpression="pk = :report_id AND begins_with(sk,:type)",
                              ExpressionAttributeValues=query_values)

    result = db_json.loads(response)["Items"]

    return result


def get_permissions_for_user(user_email):
    query_values = {
        ":report_id": {"S": user_email},
        ":type": {"S": "permission"}
    }

    response = dynamodb.query(TableName=table,
                              KeyConditionExpression="pk = :report_id AND begins_with(sk,:type)",
                              ExpressionAttributeValues=query_values)

    result = db_json.loads(response)["Items"]

    return result


def get_settings():
    query_values = {
        ":config": {"S": "config"},
        ":type": {"S": "setting_"}
    }

    response = dynamodb.query(TableName=table,
                              KeyConditionExpression="pk = :config AND begins_with(sk,:type)",
                              ExpressionAttributeValues=query_values)

    result = db_json.loads(response)["Items"]

    return result
