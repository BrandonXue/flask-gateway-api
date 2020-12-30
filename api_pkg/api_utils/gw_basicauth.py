# Third-Party Imports
from flask import Flask, request
from flask_api import status
from flask_basicauth import BasicAuth
import requests

# Local Imports
from .svc_mgr import MicroServiceManager

class GatewayBasicAuth(BasicAuth):
    # auth_exclude should be a set of paths that are public
    # and do not require authorization
    def __init__(self, app: Flask, auth_config: dict, upstream: str, svc_mgr: MicroServiceManager) -> None:
        super().__init__(app=app)
        self.__auth_exclude = auth_config['EXCLUDE']
        self.__auth_url = auth_config['AUTH_URL']
        self.__auth_svc = auth_config['AUTH_SVC']
        self.__upstream = upstream
        self.__svc_mgr = svc_mgr

    # Override authenticate so that certain urls can be excluded from authentication.
    def authenticate(self) -> bool:
        auth = request.authorization

        # If the request path is in auth_exclude, it is public and always accessible
        # This is needed to ensure that creating a new user doesn't require authentication.
        # Direct authentication at the login endpoint will skip this step because it already
        # authenticates in the request itself
        if request.path in self.__auth_exclude:
            return True
        return (
            auth and auth.type == 'basic' and
            self.check_credentials(auth.username, auth.password)
        )

    # Override check_credentials to authenticate with the users microservice
    def check_credentials(self, username, password) -> bool:
        port = self.__svc_mgr.get_worker(self.__auth_svc)
        if port == -1:
            return False
        else:
            request_url = self.__upstream + ':' + str(port) + self.__auth_url

        response = requests.request(
            'POST', request_url, 
            data = {'username':username, 'password':password}
        )
        if response.status_code == status.HTTP_200_OK:
            return True
        else:
            return False