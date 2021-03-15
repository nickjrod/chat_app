import json
import boto3
import os
import urllib3

dynamodb = boto3.client('dynamodb')


def handle(event, context):
    print(f'## EVENT: {event} ##')
    print(f'## CONTEXT: {context} ##')
    connectionId = event['requestContext']['connectionId']
    username = event['queryStringParameters'].get('username', '')
    item = {'connectionId': {'S': connectionId}, 'username': {'S': username}}
    dynamodb.put_item(TableName=os.environ['SOCKET_CONNECTIONS_TABLE_NAME'], Item=item)
    return {}
