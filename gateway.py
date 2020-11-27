# CPSC 449-02 Web Back-end Engineering

# Project 5, Polyglot Persistence (sqlite and dynamodb)

# Group members
# 		Brandon Xue (brandonx@csu.fullerton.edu)

# Inspired by <https://github.com/vishnuvardhan-kumar/loadbalancer.py>

import os
import sys

import flask
from flask_api import status, exceptions
from flask_basicauth import BasicAuth
import requests

app = flask.Flask(__name__)
app.config.from_envvar('GATEWAY_APP_CONFIG')

GATEWAY_AUTH_EXCLUDE = {
    "/api/v1/users/new",
    "/api/v1/users/login",
    "/api/v1/users/error",
    "/api/v1/timelines/error"
}
AUTHENTICATION_PATH = "/api/v1/users/login"
USERS_PATH = "/api/v1/users"
TIMELINES_PATH = "/api/v1/timelines"
DIRECT_MESSAGES_PATH = '/api/v1/dms'

UPSTREAM_URL = app.config['UPSTREAM']

users_port_RR = 0
timelines_port_RR = 0
direct_messages_port_RR = 0

users_pool = None
timelines_pool = None
direct_messages_pool = None

class GatewayBasicAuth(BasicAuth):
    # auth_exclude should be a set of paths that are public
    # and do not require authorization
    def __init__(self, app, auth_exclude, authentication_path):
        self.auth_exclude = auth_exclude
        self.authentication_path = authentication_path
        super().__init__(app=app)

    # Override authenticate so that certain urls can be excluded from authentication.
    def authenticate(self):
        auth = flask.request.authorization

        # If the request path is in auth_exclude, it is public and always accessible
        # This is needed to ensure that creating a new user doesn't require authentication.
        # Direct authentication at the login endpoint will skip this step because it already
        # authenticates in the request itself
        if flask.request.path in self.auth_exclude:
            return True
        return (
            auth and auth.type == 'basic' and
            self.check_credentials(auth.username, auth.password)
        )

    # Override check_credentials to authenticate with the users microservice
    def check_credentials(self, username, password):
        port = get_users_port()
        if port == None:
            return False
        else:
            request_url = UPSTREAM_URL + ':' + port + self.authentication_path

        response = requests.request(
            'POST', request_url, 
            data = {'username':username, 'password':password}
        )
        if response.status_code == status.HTTP_200_OK:
            return True
        else:
            return False

gateway_bauth = GatewayBasicAuth(app, GATEWAY_AUTH_EXCLUDE, AUTHENTICATION_PATH)
#gateway_bauth = BasicAuth(app)

def init_users_pool():
    global users_pool
    users_pool = [
        port for port in range(
            app.config['USERS_START_PORT'],
            app.config['USERS_START_PORT'] + app.config['USERS_PROCESS_POOL'])
    ]

def init_timelines_pool():
    global timelines_pool
    timelines_pool = [
        port for port in range(
            app.config['TIMELINES_START_PORT'],
            app.config['TIMELINES_START_PORT'] + app.config['TIMELINES_PROCESS_POOL']
        )
    ]

def init_direct_messages_pool():
    global direct_messages_pool
    direct_messages_pool = [
        port for port in range(
            app.config['DIRECT_MESSAGES_START_PORT'],
            app.config['DIRECT_MESSAGES_START_PORT'] + app.config['DIRECT_MESSAGES_PROCESS_POOL']
        )
    ]

# Return a port for the users microservice using round-robin strategy.
# Initializes the pool if not already available. Returns None if pool empty.
def get_users_port():
    global users_pool
    if users_pool == None:
        init_users_pool()
    if len(users_pool) == 0:
        return None
    global users_port_RR
    users_port_RR = (users_port_RR + 1) % len(users_pool)
    return str(users_pool[users_port_RR])

# Return a port for the timelines microservice using round-robin strategy.
# Initializes the pool if not already available. Returns None if pool empty.
def get_timelines_port():
    global timelines_pool
    if timelines_pool == None:
        init_timelines_pool()
    if len(timelines_pool) == 0:
        return None
    global timelines_port_RR
    timelines_port_RR = (timelines_port_RR + 1) % len(timelines_pool)
    return str(timelines_pool[timelines_port_RR])

# Return a port for the direct messages microservice using round-robin strategy.
# Initializes the pool if not already available. Returns None if pool empty.
def get_direct_messages_port():
    global direct_messages_pool
    if direct_messages_pool == None:
        init_direct_messages_pool()
    if len(direct_messages_pool) == 0:
        return None
    global direct_messages_port_RR
    direct_messages_port_RR = (direct_messages_port_RR + 1) % len(direct_messages_pool)
    return str(direct_messages_pool[direct_messages_port_RR])

def handle_empty_process_pool(service_type):
    return flask.json.jsonify({
        'message': service_type + " service unavailable.",
        'method': flask.request.method,
        'url': flask.request.url,
    }), exceptions.status.HTTP_503_SERVICE_UNAVAILABLE

def remove_worker(service_type, port):
    if type(port) is str:
        port = int(port)
    if service_type == 'users':
        global users_pool
        users_pool.remove(port)
    elif service_type == 'timelines':
        global timelines_pool
        timelines_pool.remove(port)
    elif service_type == 'direct_messages':
        global direct_messages_pool
        direct_messages_pool.remove(port)

@app.errorhandler(404)
@gateway_bauth.required
def route_page(err):
    if USERS_PATH in flask.request.full_path:
        service_type = 'users'
        port = get_users_port()
        if port == None:
            return handle_empty_process_pool('users')
        else:
            upstream = UPSTREAM_URL + ':' + port

    elif TIMELINES_PATH in flask.request.full_path:
        service_type = 'timelines'
        port = get_timelines_port()
        if port == None:
            return handle_empty_process_pool('timelines')
        else:
            upstream = UPSTREAM_URL + ':' + port
    elif DIRECT_MESSAGES_PATH in flask.request.full_path:
        service_type = 'direct_messages'
        port = get_direct_messages_port()
        if port == None:
            return handle_empty_process_pool('direct_messages')
        else:
            upstream = UPSTREAM_URL + ':' + port
    else:
        return flask.json.jsonify({
            'method': flask.request.method,
            'url': flask.request.url
        }), exceptions.status.HTTP_404_NOT_FOUND

    # In the API contract, authentication still uses json data
    # If our current URL is the authentication URL, we need to grab auth data
    # and put it into the json
    if flask.request.path == AUTHENTICATION_PATH:
        auth = flask.request.authorization
        request_data = {'username':auth.username, 'password':auth.password}
    else:
        request_data = flask.request.get_data()
    try:
        response = requests.request(
            flask.request.method,
            upstream + flask.request.full_path,
            data=request_data,
            headers=flask.request.headers,
            cookies=flask.request.cookies,
            stream=True,
        )
    except requests.exceptions.RequestException as e:
        app.log_exception(sys.exc_info())
        return flask.json.jsonify({
            'method': e.request.method,
            'url': e.request.url,
            'exception': type(e).__name__,
        }), exceptions.status.HTTP_500_INTERNAL_SERVER_ERROR

    headers = remove_item(
        response.headers,
        'Transfer-Encoding',
        'chunked'
    )

    # If the response was a server error response (500+),
    # Remove the process that exhibited the issue from the pool
    if response.status_code >= 500:
        remove_worker(service_type, port)
        response_dict = {
            'method': flask.request.method,
            'url': flask.request.url,
        }
        # If we're in development environment, include information on which
        # worker was removed, and what's left in the pools
        if os.environ['FLASK_ENV'] == 'development':
            global users_pool
            global timelines_pool
            response_dict['pools'] = {
                'users': users_pool,
                'timelines': timelines_pool,
                'direct_messages': direct_messages_pool
            }
            response_dict['removed'] = service_type + " " + port
        return flask.json.jsonify(response_dict), response.status_code

    return flask.Response(
        response=response.content,
        status=response.status_code,
        headers=headers,
        direct_passthrough=True,
    )


def remove_item(d, k, v):
    if k in d:
        if d[k].casefold() == v.casefold():
            del d[k]
    return dict(d)
