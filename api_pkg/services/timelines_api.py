# Third-Party Imports
import pugsql
from flask import request, g
from flask_api import status, FlaskAPI

# Local Imports
from api_pkg.api_utils import request_utils

app = FlaskAPI(__name__)
app.config.from_envvar('TIMELINES_APP_CONFIG')

queries = pugsql.module('api_pkg/services/timeline_queries/')
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
			print('Creating new users, follows, and tweets tables...')
			db.cursor().executescript(f.read())
		db.commit()
		try:
			sqlite_prefix = 'sqlite:///'
			i = app.config['DATABASE_URL'].index(sqlite_prefix) + len(sqlite_prefix)
			print('Users, follows, and tweets table created in file:', app.config['DATABASE_URL'][i:])
		except:
			pass

# Trigger a server error response
@app.route('/api/v1/timelines/error')
def trigger_error():
	if 'error' not in {*request.data}:
		error = status.HTTP_400_BAD_REQUEST
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
	try:
		auth_id = queries.authid_by_name(username=username)['id']
	except Exception as e:
		return {'error':str('Could not find user timeline.')}, status.HTTP_404_NOT_FOUND
	
	if request.method == 'GET':
		return getHomeTimeline(auth_id)
	elif request.method == 'POST':
		return postTweet(username, auth_id)
	
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
def getHomeTimeline(auth_id):
	try:
		home_timeline = queries.home_timeline(author_id=auth_id)
		return list(home_timeline)
	except Exception as e:
		return {'error':str('Could not find home timeline.')}, status.HTTP_404_NOT_FOUND

# Have a user post a tweet. This can show up on their timeline, as well as timelines
# of people who follow this user.
@request_utils.require_fields({'content_text'})
def postTweet(username, auth_id):

	try:
		inserted = queries.create_tweet(author_id=auth_id, content_text=request.data['content_text'])
		tweet = {
			'author_id': auth_id,
			'content_text': request.data['content_text'],
			'id': queries.recent_tweet_id(author_id=auth_id)["id"]
		}
	except Exception as e:
		return {'error':str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
		
	return tweet, status.HTTP_201_CREATED, {
		'Location': f'/api/v1/timelines/{username}'
	}	
