import json
import boto3
import os

dynamodb = boto3.client('dynamodb')


def broadcast_disconnection(event, username, disconnecting_id):
    """Broadcast that the user has disconnected to every connection in the DB. """
    full_message = f'{username} has disconnected.'
    paginator = dynamodb.get_paginator('scan')

    connectionIds = []

    apigatewaymanagementapi = boto3.client(
        'apigatewaymanagementapi',
        endpoint_url="https://" + event["requestContext"]["domainName"] + "/" + event["requestContext"]["stage"])

    # Retrieve all connectionIds from the database
    for page in paginator.paginate(TableName=os.environ['SOCKET_CONNECTIONS_TABLE_NAME']):
        connectionIds.extend(page['Items'])
    # Emit the recieved message to all the connected devices
    for connectionIdObj in connectionIds:
        connectionId = connectionIdObj['connectionId']['S']
        if connectionId != disconnecting_id:
            apigatewaymanagementapi.post_to_connection(
                Data=full_message,
                ConnectionId=connectionId)


def handle(event, context):
    connection_id = event['requestContext']['connectionId']
    # Delete connectionId from the database
    table_name = os.environ['SOCKET_CONNECTIONS_TABLE_NAME']
    item_key = {'connectionId': {'S': connection_id}}
    item = dynamodb.get_item(TableName=table_name, Key=item_key)
    username = item['Item']['username']['S']

    dynamodb.delete_item(TableName=table_name, Key=item_key)

    # Alert everyone else in chatroom that user has disconnected.
    broadcast_disconnection(event, username, connection_id)
    return {}
