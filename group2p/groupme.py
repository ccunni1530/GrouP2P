import requests
from enum import Enum

class GroupMeException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)

class GroupMeAPI:
    """
    Handler for HTTP requests to the GroupMe API
    """
    URL = "https://api.groupme.com/v3/"
    _token = ""
    _connection = None

    def __init__(self, token: str):
        """
        Initializes a connection to the GroupMe API using an access token.

        :param token: The access token to be used
        :type token: str
        """
        self._token = token
        self._connection = requests.get(url=f"{self.URL}users/me?token={token}")
        if self._connection.status_code != 200: raise GroupMeException(f"Failed to initialize with token ({token}): HTTP Error {self._connection.status_code}.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass
    
    @property
    def user(self) -> str:
        """
        Returns the ID of the user whose token was used for initialization.

        :returns: The user ID
        :rtype: str
        """
        info = self.get("users/me")
        userid = "-1"
        if info.status_code == 200:
            userid = info.json()["response"]["id"]
        else:
            raise GroupMeException(f"HTTP error ({info.status_code})")
        return userid

    def get(self, _call: str, _params=None) -> requests.Response:
        """
        Makes a GET request to the GroupMe API

        :param _call: The URL rule being called
        :type _call: str
        :param _params: Parameters to be attached to the HTTP request
        :type _params: iterable
        :returns: A Response object containing requested information.
        :rtype: requests.Response
        """
        return requests.get(url=f"{self.URL}{_call}?token={self._token}", params=_params)

    def post(self, _call: str, _params=None) -> requests.Response:
        """
        Makes a POST request to the GroupMe API

        :param _call: The URL rule being called
        :type _call: str
        :param _params: Parameters to be attached to the HTTP request
        :type _params: iterable
        :returns: A Response object containing requested information.
        :rtype: requests.Response
        """
        return requests.post(url=f"{self.URL}{_call}?token={self._token}", params=_params)
