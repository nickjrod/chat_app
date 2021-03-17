import boto3
import os
import botocore.exceptions as exceptions

dynamodb = boto3.client('dynamodb')


def broadcast_connection(event, username, connecting_id):
    """Broadcast that the user has connected to every connection in the DB. """
    full_message = f'{username} has connected.'
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
        if connectionId != connecting_id:
            apigatewaymanagementapi.post_to_connection(
                Data=full_message,
                ConnectionId=connectionId
            )


def handle(event, context):
    # Add new connection/user to the DB
    connectionId = event['requestContext']['connectionId']
    username = event['queryStringParameters'].get('username', '')
    item = {'connectionId': {'S': connectionId}, 'username': {'S': username}}
    dynamodb.put_item(TableName=os.environ['SOCKET_CONNECTIONS_TABLE_NAME'], Item=item)

    # Alert everyone else in chatroom that new user has connected.
    broadcast_connection(event, username, connectionId)

    return {}
