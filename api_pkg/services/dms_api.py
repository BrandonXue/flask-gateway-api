# Standard Imports
from datetime import datetime

# Third-Party Imports
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from flask import request
from flask_api import FlaskAPI, exceptions, status

# Local Imports
from api_pkg.services import dms_schema
# import request_utils
from api_pkg.api_utils import request_utils


app = FlaskAPI(__name__)
app.config.from_envvar('DIRECT_MESSAGES_APP_CONFIG')
DM_TABLE_NAME = 'dms'

boto_client = boto3.client('dynamodb', endpoint_url=app.config['DYNAMODB_URL'])
dynamodb = boto3.resource('dynamodb', endpoint_url=app.config['DYNAMODB_URL'])
dm_table = dynamodb.Table(DM_TABLE_NAME)

@app.cli.command('init')
def init_db():
	# Get the service resource.
	global boto_client
	global dynamodb 
	all_tables = boto_client.list_tables(Limit=100)
	try:
		all_tables['TableNames'].index(DM_TABLE_NAME)
		print('Previous direct messages table found. Deleting table...')
		boto_client.delete_table(TableName=DM_TABLE_NAME)
	except:
		print('No previous direct messages table found.')

	print('Creating new direct messages table...')

	# Create the DynamoDB table.
	# t = to
	# fr = from
	# ts = timestamp
	# irt = in-reply-to
	# msg = message
	# qro = quick-reply-options
	# mId = messageId
	table = dynamodb.create_table(**(dms_schema.dm_table_schema)) # in dms_schema.py
	# Wait until the table exists.
	table.meta.client.get_waiter('table_exists').wait(TableName=DM_TABLE_NAME)
	print("New direct messages table created with name:", table.name)

	# Populate some test data
	item1 = {
		't': 'user1',
		'fr': 'user2',
		'ts': '2020-11-27T12:54:59.540514',
		'mId': '2020-11-27T12:54:59.540514user2',
		'msg': 'Hey user1!',
	}

	item2 = {
		't': 'user2',
		'fr': 'user1',
		'irt': '2020-11-27T12:54:59.540514user2',
		'ts': '2020-11-27T12:55:39.410569',
		'mId': '2020-11-27T12:55:39.410569user1',
		'msg': 'hi'
	}

	item3 = {
		't': 'user1',
		'fr': 'user2',
		'ts': '2020-11-27T12:56:13.848139',
		'mId': '2020-11-27T12:56:13.848139user2',
		'msg': 'Would you like to sign up to our website?',
		'qro': ['Yes please, I\'m interested!', 'No, thank you!']
	}

	try:
		response1 = dm_table.put_item(Item=item1)
		response2 = dm_table.put_item(Item=item2)
		response3 = dm_table.put_item(Item=item3)
	except ClientError: # If key somehow already exists or some other error occurs
		print("Uh oh, something went wrong!")

	
@app.route('/api/v1/dms', methods=['GET', 'POST'])
def handle_direct_message():
	if request.method == 'POST':
		return send_direct_message()
	elif request.method == 'GET':
		return list_direct_messages_for()

@request_utils.require_fields({'to', 'message'})
def send_direct_message():
	global dm_table
	sender = request.authorization.username

	posted_fields = {*request.data}

	# Disallow masquerading as other users
	if 'from' in posted_fields and request.data['from'] != sender:
		return {
			'message': 'Cannot specify a \'from\' that is different from provided authorization.'
		}, status.HTTP_401_UNAUTHORIZED

	# Ideally we would check that the other user exists, but for the purpose of this assignment no check.

	data_to = request.data['to']
	data_timestamp = datetime.utcnow().isoformat()
	data_msg_id = data_timestamp + sender
	data_message = request.data['message']
	item = {
		't': data_to,
		'fr': sender,
		'ts': data_timestamp,
		'mId': data_msg_id,
		'msg': data_message,
	}
	if 'quickreply' in posted_fields and len(request.data['quickreply']) > 0:
		item['qro'] = request.data['quickreply']

	try:
		response = dm_table.put_item(
			Item=item,
			ConditionExpression='attribute_not_exists(mId)'
		)
	except ClientError: # If key somehow already exists or some other error occurs
		return {'message': 'Message not created.'}, exceptions.status.HTTP_500_INTERNAL_SERVER_ERROR


	return {
		'to': data_to,
		'from': sender,
		'messageId': data_msg_id,
		'timestamp': data_timestamp
	}, status.HTTP_201_CREATED, {
		'Location': '/api/v1/dms/' + data_msg_id
	}

def list_direct_messages_for():
	global dm_table
	recipient = request.authorization.username # Can only request inbox for authenticated user
	posted_fields = {*request.data}

	if 'to' in posted_fields and request.data['to'] != recipient:
		return {
			'message': 'Cannot specify a \'to\' that is different from provided authorization.'
		}, status.HTTP_401_UNAUTHORIZED

	try:
		if 'timestamp' in posted_fields: # timestamp given
			response = dm_table.query(
				Select='ALL_ATTRIBUTES',
				Limit=100,
				KeyConditionExpression=Key('t').eq(recipient),
				FilterExpression=Key('ts').gte(request.data['timestamp'])
			)
		else: # No timestamp given
			response = dm_table.query(
				Select='ALL_ATTRIBUTES',
				Limit=100,
				KeyConditionExpression=Key('t').eq(recipient)
			)
	except ClientError:
		return {'message': 'Error on query.'}, exceptions.status.HTTP_500_INTERNAL_SERVER_ERROR
	
	# Hide metadata and internal information from API user
	metadata = response.pop('ResponseMetadata', None)
	scanned_count = response.pop('ScannedCount', None)
	return response, status.HTTP_200_OK

@app.route('/api/v1/dms/<string:original>/replies', methods=['GET', 'POST'])
def handle_replies(original):
	if request.method == 'GET':
		return list_replies_to(original)
	else:
		return reply_to_direct_message(original)

def list_replies_to(original):
	global dm_table
	username = request.authorization.username
	posted_fields = {*request.data}

	try:
		if 'timestamp' in posted_fields: # timestamp given
			response = dm_table.query(
				TableName=DM_TABLE_NAME,
				IndexName='replies',
				Select='ALL_ATTRIBUTES',
				Limit=100,
				KeyConditionExpression=Key('irt').eq(original),
				FilterExpression=Key('ts').gte(request.data['timestamp'])
			)
		else: # No timestamp given
			response = dm_table.query(
				TableName=DM_TABLE_NAME,
				IndexName='replies',
				Select='ALL_ATTRIBUTES',
				Limit=100,
				KeyConditionExpression=Key('irt').eq(original)
			)
	except ClientError:
		return {'message': 'Error on query.'}, exceptions.status.HTTP_500_INTERNAL_SERVER_ERROR
	
	# Hide metadata and internal information from API user
	metadata = response.pop('ResponseMetadata', None)
	scanned_count = response.pop('ScannedCount', None)
	return response, status.HTTP_200_OK

@request_utils.require_fields({'message'})
def reply_to_direct_message(original):
	global dm_table

	sender = request.authorization.username
	posted_fields = {*request.data}
	if 'from' in posted_fields and request.data['from'] != sender:
		return {
			'message': 'Cannot specify a \'from\' that is different from provided authorization.\n'
			'You do not need to specify \'from\' other than by providing authentication.'
		}, status.HTTP_401_UNAUTHORIZED
	
	# Make sure a message with the origina messageId exists
	response = dm_table.query(
			TableName=DM_TABLE_NAME,
			IndexName='messageIds',
			Select='ALL_PROJECTED_ATTRIBUTES',
			Limit=100,
			KeyConditionExpression=Key('mId').eq(original)
	)

	if response['Count'] == 0:
		return {
			'message': 'The message you are trying to reply to does not exist.'
		}, status.HTTP_404_NOT_FOUND

	data_to = response['Items'][0]['t']
	data_timestamp = datetime.utcnow().isoformat()
	data_msg_id = data_timestamp + sender
	data_message = request.data['message']
	item = {
		't': data_to,
		'fr': sender,
		'ts': data_timestamp,
		'mId': data_msg_id,
		'msg': data_message,
		'irt': original
	}

	try:
		dm_table.put_item(
			Item=item
		)
	except ClientError: # If key somehow already exists or some other error occurs
		return {'message': 'Reply not created.'}, exceptions.status.HTTP_500_INTERNAL_SERVER_ERROR

	return {'timestamp': data_timestamp}, status.HTTP_201_CREATED, {
		'Location': '/api/v1/dms/' + original + '/replies'
	}