from core.database.db import dynamodb, table, reverseIndex, delete_item, put_item_unique_pk, get_item, get_items_by_type, put_item_no_check
from dynamodb_json import json_util as db_json
import json


def get_report_entries(report_id):
    query_values = {
        ":report_id": {"S": report_id},
        ":type": {"S": "entry"}
    }

    response = dynamodb.query(TableName=table,
                              KeyConditionExpression="pk = :report_id AND begins_with(sk,:type)",
                              ExpressionAttributeValues=query_values)

    result = db_json.loads(response)["Items"]

    return result


def get_report_entries_for_user(report_id, user_id):
    query_values = {
        ":report_id": {"S": report_id},
        ":type": {"S": "entry_%s_" % user_id}
    }

    response = dynamodb.query(TableName=table,
                              KeyConditionExpression="pk = :report_id AND begins_with(sk,:type)",
                              ExpressionAttributeValues=query_values)

    result = db_json.loads(response)["Items"]

    return result


def checkReportEntryForUser(report_id, user_id, description = None):
    entries = get_report_entries_for_user(report_id, user_id)

    if description is None:
        return entries

    if len(entries) == 0:
        return entries

    for entry in entries:
        if entry["description"] == description:
            return entry

    return []