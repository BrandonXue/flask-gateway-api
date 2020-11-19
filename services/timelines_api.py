# CPSC 449-02 Web Back-end Engineering

# Project 2, RESTful Microservices

# Group members
# 		Jacob Rapmund (jacobwrap86@csu.fullerton.edu)
# 		Brandon Xue (brandonx@csu.fullerton.edu)

import flask_api
from flask import request, g
from flask_api import status, exceptions
import pugsql

app = flask_api.FlaskAPI(__name__)
app.config.from_envvar('TIMELINES_APP_CONFIG')

queries = pugsql.module('services/timeline_queries/')
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
@app.route('/api/v1/timelines/error')
def trigger_error(error):
	if 'error' not in {*request.data}:
		error = 404
	else:
		error = request.data['error']
		
	return {
		"error": "This endpoint is used for development purposes."
		}, error

# Placeholder for root, return text saying "Home Page"
@app.route('/api/v1/timelines', methods=['GET'])
def home():
	return getPublicTimeline()

# Get a public timeline. This contains all the tweets in the database.
@app.route('/api/v1/timelines/public', methods=['GET'])
def getPublicTimeline():
	all_tweets=queries.all_tweets()
	return list(all_tweets)
	
# Handle the endpoint for a user's home timeline. This includes getting
# up to 25 tweets by people this user is following, and making posts.
@app.route('/api/v1/timelines/<string:username>/home', methods=['GET', 'POST'])
def homeTimeline(username):
	if request.method == 'GET':
		return getHomeTimeline(username)
	elif request.method == 'POST':
		return postTweet(username, request.data)
	
# Get up to 25 tweets posted by a particular user.
@app.route('/api/v1/timelines/<string:username>', methods=['GET'])
def getUserTimeline(username):
	username = username.replace(" ", "")
	try:
		author_id = queries.authid_by_name(username=username)['id']
	except Exception as e:
		return {'error':str("User: "+username+" not found.")}, status.HTTP_404_NOT_FOUND
	user_tweets=queries.user_tweets(author_id=author_id)
	return list(user_tweets)
	

# Get a user's home timeline. This consists of up to 25 of the most recent
# posts made by users this user is following.
def getHomeTimeline(username):
	username = username.replace(" ", "")
	try:
		author_id = queries.authid_by_name(username=username)['id']
		home_timeline = queries.home_timeline(author_id=author_id)
		return list(home_timeline)
	except Exception as e:
		return {'error':str('Could not verify user.')}, status.HTTP_401_UNAUTHORIZED

# Have a user post a tweet. This can show up on their timeline, as well as timelines
# of people who follow this user.
def postTweet(username, text):
	username = username.replace(" ", "")
	
	if not username or not text:
		message = f'Error: Missing fields'
		raise exceptions.ParseError(message)
		
	try:
		tweet = {'author_id':queries.authid_by_name(username=username)['id'],'content_text':text['content_text']}
	except Exception as e:
		return {'error':str('Could not verify user.')}, status.HTTP_401_UNAUTHORIZED
		
	try:
		queries.create_tweet(**tweet)
		tweet['id'] = queries.recent_tweet_id(author_id=tweet['author_id'])["id"]
	except Exception as e:
		return {'error':str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
		
	return tweet, status.HTTP_201_CREATED, {
		'Location': f'/api/v1/timelines/{username}'
	}	
