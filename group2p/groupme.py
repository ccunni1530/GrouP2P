import json
import requests
from enum import Enum

class GroupMeException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)

class GroupMeAPI:
    """
    Used to connect to GroupMe servers and 
    """
    STATUS = Enum("STATUS", "OFF DISCONNECTED CONNECTED ERROR")
    URL = "https://api.groupme.com/v3/"
    _token = ""
    _status = ""
    _connection = None

    def __init__(self, token: str):
        self._token = token
        self._status = self.STATUS
        self._connection = requests.get(url=f"{self.URL}users/me?token={token}")
        if self._connection.status_code != 200: raise GroupMeException(f"Failed to initialize ({self._connection.status_code}).")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

    @property
    def status(self):
        return self._status
    
    @property
    def user(self):
        info = requests.get(url=f"{self.URL}?token={self._token}")
        userid = "-1"
        if info.status_code == 200:
            userid = info.json()["id"]
        else:
            raise GroupMeException(f"HTTP error ({self._connection.status_code})")
        return userid

    def get(self, _call: str, _params=None):
        return requests.get(url=f"{self.URL}{_call}?token={self._token}", params=_params)

    def post(self, _call: str, _params=None):
        return requests.post(url=f"{self.URL}{_call}?token={self._token}", params=_params)
