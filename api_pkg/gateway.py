# Inspired by <https://github.com/vishnuvardhan-kumar/loadbalancer.py>

# Standard Imports
import os
import sys

# Third-Party Imports
from flask import Flask, request, Response
from flask_api import status, exceptions
import requests

# Local Imports
from .api_utils.svc_mgr import MicroServiceManager
from .api_utils.gw_basicauth import GatewayBasicAuth

app = Flask(__name__)
app.config.from_envvar('GATEWAY_APP_CONFIG')

svc_mgr = MicroServiceManager(app.config['SVC_CONFIG'])
gateway_bauth = GatewayBasicAuth(app, app.config['AUTH_CONFIG'], app.config['UPSTREAM'], svc_mgr)

def handle_empty_process_pool(service_type: str):
    return {
        'message': service_type.casefold() + " service unavailable.",
        'method': request.method,
        'url': request.url,
    }, exceptions.status.HTTP_503_SERVICE_UNAVAILABLE

@app.errorhandler(404)
@gateway_bauth.required
def route_page(err):
    service_type = svc_mgr.get_service_type(request.full_path)

    # If no matching service was found
    if service_type == "":
        return {
            'url': request.url
        }, exceptions.status.HTTP_404_NOT_FOUND

    port = svc_mgr.get_worker(service_type)
    
    # If no instances are left for this service type
    if port == -1:
        return handle_empty_process_pool(service_type)

    upstream = app.config['UPSTREAM'] + ':' + str(port)

    # In the API contract, authentication still uses json data
    # If our current URL is the authentication URL, we need to grab auth data
    # and put it into the json
    if request.path == app.config['AUTH_CONFIG']['AUTH_URL']:
        auth = request.authorization
        request_data = {'username':auth.username, 'password':auth.password}
    else:
        request_data = request.get_data()
    try:
        response = requests.request(
            request.method,
            upstream + request.full_path,
            data=request_data,
            headers=request.headers,
            cookies=request.cookies,
            stream=True,
        )
    except requests.exceptions.RequestException as e:
        app.log_exception(sys.exc_info())
        return {
            'method': e.request.method,
            'url': e.request.url,
            'exception': type(e).__name__,
        }, exceptions.status.HTTP_500_INTERNAL_SERVER_ERROR

    headers = remove_item(
        response.headers,
        'Transfer-Encoding',
        'chunked'
    )

    # If the response was a server error response (500+),
    # Remove the process that exhibited the issue from the pool
    if response.status_code >= 500:
        svc_mgr.remove_worker(service_type, port)
        response_dict = {
            'method': request.method,
            'url': request.url,
        }
        # If we're in development environment, include information on which
        # worker was removed, and what's left in the pools
        if os.environ['FLASK_ENV'] == 'development':
            response_dict['status'] = response.status_code
            response_dict['pools'] = svc_mgr.get_pools()
            response_dict['removed'] = service_type + " " + str(port)
        return response_dict, status.HTTP_500_INTERNAL_SERVER_ERROR

    return Response(
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
