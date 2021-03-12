import json
import boto3
import os

dynamodb = boto3.client('dynamodb')


def handle(event, context):
	connectionId = event['requestContext']['connectionId']
	
	# Delete connectionId from the databaseNAME
	table_name = os.environ['SOCKET_CONNECTIONS_TABLE_NAME']
	key = {'connectionId': {'S': connectionId}}
	dynamodb.delete_item(TableName=table_name, Key=key)
	
	return {}
