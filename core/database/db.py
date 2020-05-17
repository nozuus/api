import boto3
import os
import json
from dynamodb_json import json_util as db_json

stage = os.environ.get("stage")

if not stage:
    stage = "dev"
table = "OtterPondTable-%s" % stage
reverseIndex = "OtterPondTable-Reverse-%s" % stage

dynamodb = None
if stage == "dev":
    key = os.environ.get("aws_key")
    secret = os.environ.get("aws_secret")
    dynamodb = boto3.client("dynamodb", aws_access_key_id=key, aws_secret_access_key=secret, region_name='us-east-1')
else:
    dynamodb = boto3.client('dynamodb')


# Shared Functions

def delete_item(pk, sk):
    query = {
        "pk": {"S": pk},
        "sk": {"S": sk}
    }

    response = dynamodb.delete_item(TableName=table,
                                    Key=query)

    return response["ResponseMetadata"]["HTTPStatusCode"] == 200


def put_item_no_check(item_obj):
    item = json.loads(db_json.dumps(item_obj))

    response = dynamodb.put_item(TableName=table,
                                 Item=item)

    return response["ResponseMetadata"]["HTTPStatusCode"] == 200


def put_item_unique_pk(item_obj):
    item = json.loads(db_json.dumps(item_obj))

    response = dynamodb.put_item(TableName=table,
                                 Item=item,
                                 ConditionExpression="attribute_not_exists(pk)")

    return response["ResponseMetadata"]["HTTPStatusCode"] == 200


def get_item(pk, sk):
    query_values = {
        ":primary": {"S": pk},
        ":secondary": {"S": sk},
    }

    response = dynamodb.query(TableName=table,
                              KeyConditionExpression="pk = :primary AND sk = :secondary",
                              ExpressionAttributeValues=query_values)

    result = db_json.loads(response)["Items"]

    if len(result) > 0:
        return result[0]
    return None


def get_items_by_type(type):
    query_values = {
        ":type": {"S": type}
    }

    response = dynamodb.query(TableName=table,
                              IndexName=reverseIndex,
                              KeyConditionExpression="sk = :type",
                              ExpressionAttributeValues=query_values)

    result = db_json.loads(response)["Items"]

    return result


def get_items_for_pk_by_type(pk, type):
    query_values = {
        ":key": {"S": pk},
        ":type": {"S": "%s_" % type}
    }

    response = dynamodb.query(TableName=table,
                              KeyConditionExpression="pk = :key AND begins_with(sk,:type)",
                              ExpressionAttributeValues=query_values)
    return db_json.loads(response)["Items"]
