# CPSC 449-02 Web Back-end Engineering

# Project 2, RESTful Microservices

# Group members
# 		Jacob Rapmund (jacobwrap86@csu.fullerton.edu)
# 		Brandon Xue (brandonx@csu.fullerton.edu)

import flask_api
from flask import request, g
from flask_api import status, exceptions
import pugsql
import werkzeug.security as wk_s

CRYPT_HASH_ALGORITHM = 'sha3_512'
PASSWORD_SALT_LENGTH = 64

app = flask_api.FlaskAPI(__name__)
app.config.from_envvar('USERS_APP_CONFIG')

queries = pugsql.module('services/user_queries/')
queries.connect(app.config['DATABASE_URL'])

# Get a database Engine object
def get_db():
	db = getattr(g,'_database', None)
	if db is None:
		db = g._database = queries.engine.raw_connection()
	return db

# Close the database connection if necessary
@app.teardown_appcontext
def close_connection(exception):
	db = getattr(g, '_database', None)
	if db is not None:
		db.close()

# Initialize the database and populate it with some example data.
# For testing purposes all test users' passwords are simply 'password'
@app.cli.command('init')
def init_db():
	with app.app_context():
		db = get_db()
		with app.open_resource('MBS.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

# Trigger a server error response
@app.route('/api/v1/users/error')
def trigger_error():
	if 'error' not in {*request.data}:
		error = 404
	else:
		error = request.data['error']
	
	return {
		"error": "This endpoint is used for development purposes."
		}, error

# Placeholder for root, show all users' usernames in the database
@app.route('/api/v1/users', methods=['GET'])
def home():
	all_users = queries.all_users()
	return [user['username'] for user in all_users]

# Create a new user
@app.route('/api/v1/users/new', methods=['POST'])
def createUser():
	posted_fields = {*request.data}
	required_fields = {'username', 'email', 'password'}
	
	# Check that all required fields are provided. Extras are ignored
	if not required_fields <= posted_fields:
		message = f'Missing fields: {required_fields - posted_fields}'
		raise exceptions.ParseError(message)

	username = request.data['username']
	email = request.data['email']
	password = request.data['password']

	# Check if username and email are already in use
	with queries.transaction():
		if queries.user_exists(user_name=username): # See if username exists
			return {'message': "Username already exists."}, status.HTTP_409_CONFLICT
		if queries.email_exists(user_email=email): # See if email is already in use
			return {'message': "Email is already in use."}, status.HTTP_409_CONFLICT
		try:
			hashed_pw = wk_s.generate_password_hash(password, CRYPT_HASH_ALGORITHM, PASSWORD_SALT_LENGTH)
			queries.create_user(user_name=username, user_email=email, pw_hash=hashed_pw)
		except Exception as e: # Unknown conflict error
			return {'message':str(e)}, status.HTTP_409_CONFLICT
		
	return request.data, status.HTTP_201_CREATED, {
		'Location': f'/api/v1/users/{request.args.get("username")}'
	}

# Authenticate a user
@app.route('/api/v1/users/login', methods=['POST'])
def authenticateUser():
	posted_fields = {*request.data}
	required_fields = {'username', 'password'}
	
	# Check if all reqiured fields are provided. Extras are ignored
	if not required_fields <= posted_fields:
		message = f'Missing fields: {required_fields - posted_fields}'
		raise exceptions.ParseError(message)

	username = request.data['username']
	password = request.data['password']

	pw_hash = queries.find_hash(user_name=username)

	if wk_s.check_password_hash(pw_hash, password):
		return {
			'message': 'Authentication successful.'
		}, status.HTTP_200_OK, {
			'Location': (f'/api/v1/users/' + username)
		}
	else:
		msg = "Username or password was incorrect."
		raise exceptions.AuthenticationFailed(detail=msg)

# Handle API endpoint for addFollower and removeFollower
@app.route('/api/v1/users/<string:username>/follows', methods=['POST', 'DELETE'])
def followers(username):
	# Check if user exists
	if not queries.user_exists(user_name=username):
		raise exceptions.NotFound("Current user not found.")

	posted_fields = {*request.data}
	required_fields = {'follow'}
	
	# Check if all reqiured fields are provided. Extras are ignored
	if not required_fields <= posted_fields:
		message = f'Missing fields: {required_fields - posted_fields}'
		raise exceptions.ParseError(message)

	user_followed = request.data['follow']

	if request.method == 'POST':
		return addFollower(username, user_followed)
	elif request.method == 'DELETE':
		return removeFollower(username, user_followed)

# Add a follow relationship if both users exist and the relationship doesn't exist
def addFollower(username, usernameToFollow):
	with queries.transaction():
		if not queries.user_exists(user_name=username):
			raise exceptions.NotFound("The current user no longer exists.")
		if not queries.user_exists(user_name=usernameToFollow):
			raise exceptions.NotFound("The user you are trying to follow no longer exists.")
		try:
			queries.add_follower(user_name=username, followed_name=usernameToFollow)
		except Exception as e:
			return {'message': 'You are already following this user.'}, status.HTTP_409_CONFLICT
		
	return request.data, status.HTTP_201_CREATED

# Remove a follow relationship if both users exist and the relationship exists
def removeFollower(username, usernameToRemove):
	with queries.transaction():
		if not queries.user_exists(user_name=username):
			raise exceptions.NotFound("The current user no longer exists.")
		if not queries.user_exists(user_name=usernameToRemove):
			raise exceptions.NotFound("The user you are trying to unfollow no longer exists.")
		if queries.remove_follower(user_name=username, followed_name=usernameToRemove):
			return request.data, status.HTTP_200_OK
		else:
			raise exceptions.NotFound("Could not unfollow: the follower relationship does not exist.")