from core.database.db import dynamodb,table,reverseIndex, delete_item, get_item, put_item_no_check
from dynamodb_json import json_util as db_json
import json
import datetime


def create_user(user):
    item = json.loads(db_json.dumps(user))

    response = dynamodb.put_item(TableName=table,
                                 Item=item,
                                 ConditionExpression="attribute_not_exists(pk)")

    return response["ResponseMetadata"]["HTTPStatusCode"] == 200


def get_user_by_email(user_email):
    query_values = {
        ":user_email": {"S": user_email},
        ":type": {"S": "user"}
    }

    response = dynamodb.query(TableName=table,
                              KeyConditionExpression="pk = :user_email AND sk = :type",
                              ExpressionAttributeValues=query_values)

    result = db_json.loads(response)["Items"]

    if len(result) > 0:
        return result[0]
    return None


def get_all_users():
    query_values = {
        ":type": {"S": "user"}
    }

    response = dynamodb.query(TableName=table,
                              IndexName=reverseIndex,
                              KeyConditionExpression="sk = :type",
                              ExpressionAttributeValues=query_values)

    result = db_json.loads(response)["Items"]

    return result


def update_user(user):
    item = json.loads(db_json.dumps(user))

    response = dynamodb.put_item(TableName=table,
                                 Item=item)

    return response["ResponseMetadata"]["HTTPStatusCode"] == 200


def set_password_reset_token(user_email, token, expiration):
    item = json.loads(db_json.dumps({
        "pk": user_email,
        "sk": "resetToken",
        "token": token,
        "expiration": expiration
    }))

    response = dynamodb.put_item(TableName=table,
                                 Item=item)

    return response["ResponseMetadata"]["HTTPStatusCode"] == 200


def get_user_token(user_email):
    query_values = {
        ":email": {"S": user_email},
        ":type": {"S": "resetToken"}
    }

    response = dynamodb.query(TableName=table,
                              KeyConditionExpression="pk = :email AND sk = :type",
                              ExpressionAttributeValues=query_values)


    result = db_json.loads(response)["Items"]

    if len(result) > 0:
        return result[0]

    return None


def get_user_permissions(user_email):
    query_values = {
        ":email": {"S": user_email},
        ":type": {"S": "permission"}
    }

    response = dynamodb.query(TableName=table,
                              KeyConditionExpression="pk = :email AND begins_with(sk, :type)",
                              ExpressionAttributeValues=query_values)

    result = db_json.loads(response)["Items"]

    return result


def get_existing_gtid(user_email):
    query_values = {
        ":email": {"S": user_email},
        ":type": {"S": "gtid"}
    }

    response = dynamodb.query(TableName=table,
                              KeyConditionExpression="pk = :email AND begins_with(sk, :type)",
                              ExpressionAttributeValues=query_values)

    result = db_json.loads(response)["Items"]

    if len(result) > 0:
        return result[0]
    return None


def get_user_by_gtid(hashed_gtid):
    query_values = {
        ":gtid": {"gtid_" + hashed_gtid}
    }

    response = dynamodb.query(TableName=table,
                              IndexName=reverseIndex,
                              KeyConditionExpression="sk = :gtid",
                              ExpressionAttributeValues=query_values)

    result = db_json.loads(response)["Items"]

    if len(result) > 0:
        return result[0]["pk"]

    return None