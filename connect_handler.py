import json
import boto3
import os

dynamodb = boto3.client('dynamodb')


def handle(event, context):
    connectionId = event['requestContext']['connectionId']
    item = {'connectionId': {'S': connectionId}}
    dynamodb.put_item(TableName=os.environ['SOCKET_CONNECTIONS_TABLE_NAME'], Item=item)
    return {}
