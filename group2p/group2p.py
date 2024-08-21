import json
from groupme import *
from os import path
from threading import Thread
from time import monotonic

CONFIG_FILENAME = "config.json"

class GrouP2P:
    """
    Primary handler for interactions between GroupMe and the app
    using the service. Makes all calls necessary to the API and
    receives responses.
    """
    _encoding = None
    _msgHistory = None
    _user = {
        "connection": None
    }
    
    def __init__(self, token=""):
        self._msgHistory = list()

        if path.exists(CONFIG_FILENAME) and token == "":
            with open(CONFIG_FILENAME, "r") as f:
                try:
                    settings = json.loads(f.read())
                    token = settings["token"]
                    if not token: raise KeyError
                except KeyError:
                    token = input("An error occurred when attempting to read token from file. Please re-enter: ")
                except json.JSONDecodeError as e:
                    print(f"An error occured while trying to load the config: {e}")
        elif token == "":
            token = input("Enter GroupMe Developer token: ")
                
        self._user["connection"] = GroupMeAPI(token)
        self._msgHistory = dict()
        self._encoding = str.encode

    @property
    def config(self):
        """:returns: The config file settings as a dictionary."""
        with open(CONFIG_FILENAME, "r") as f:
            return json.loads(f.read())
        
    @property
    def userID(self):
        """:returns: The user's ID."""
        return self._user["connection"].user

    def set_config(self, option: str, value):
        """
        Sets a config option and writes it to file.

        :returns: The updated settings as a dictionary.
        """
        settings = dict()
        if path.exists(path.join(path.abspath(path.dirname(__file__)), CONFIG_FILENAME)):
            with open(CONFIG_FILENAME, "r") as f:
                try:
                    settings = json.loads(f.read())
                except json.JSONDecodeError as e:
                    print(f"Failed to parse JSON: {e}")

        with open(CONFIG_FILENAME, "w") as f:
            settings[option] = value
            f.write(json.dumps(settings))
        
        return settings
    
    def get_config(self, option: str):
        """
        Gets a specified option from the config file.

        :returns: The option requested, or None if the option wasn't found.
        """
        try:
            with open(CONFIG_FILENAME, "r") as f:
                settings = json.loads(f.read())
                return settings[option]
        except KeyError:
            return None

    def set_encoding(self, encodingFunc):
        self._encoding = encodingFunc

    def create_group(self, name="GrouP2P", users=None, share=True):
        """
        Starts a chat with the passed userIDs added.

        :returns: The server response.
        """
        with self._user["connection"] as c:
            params = dict()
            params["share"] = share
            params["name"] = name
            r = c.post("groups", params)
            response = r.json()
            groupID = response["response"]["id"]
            self._msgHistory[groupID] = list()

            if users:
                params.clear()
                params["members"] = list()
                for user,pos in enumerate(users):
                    member = {
                            "nickname": ("player" + str(pos+1)),
                            "user_id": user
                    }
                    params["members"].append()
                c.post(f"groups/{groupID}/members/add", params)

            return r

    def delete_group(self, groupID: str):
        """"
        Deletes the specified group (must be creator).

        :returns: The server response.
        """
        with self._user["connection"] as c:
            return c.post(f"groups/{groupID}/destroy")

    def join_group(self, groupID: str, shareToken: str):
        """
        Join the user to the specified group using the provided
        share token. Fails if the share token is invalid.

        :returns: The server response.
        """
        with self._user["connection"] as c:
            return c.post(f"groups/{groupID}/join/{shareToken}")

    def send(self, data: str, groupID: str):
        """
        Sends a message to the specified group containing the
        provided data. Encodes the message into bytes and uses
        proprietary format to distinguish grouP2P messages from
        other kinds.

        :returns: The server response.
        """
        msg = Message(self._user["player"], data, self._encoding)
        with self._user["connection"] as c:
            params = dict()
            params["source_guid"] = str(monotonic())[-5:]
            params["text"] = msg
            r = c.post(f"/groups/{groupID}/messages", params)

        return r

    def receive(self, groupID: str, limit=20):
        """
        Checks the group for any new messages and updates the history
        stored. Gets up to and including the (limit)th most recent
        message since the last known message.

        :returns: A list of all new messages.
        """
        with self._user["connection"] as c:
            params = dict()
            if groupID in self._msgHistory.keys() and len(self._msgHistory[groupID]) > 0:
                params["since_id"] = self._msgHistory[groupID][0]["id"]
            params["limit"] = limit
            
            r = c.get(f"groups/{groupID}/messages", params)
            if r.status_code == 304: return list()
            r = r.json()
            messages = r["response"]["messages"]

            if groupID not in self._msgHistory.keys():
                self._msgHistory[groupID] = list()
            
            newMessages = list()
            for msg in messages:
                self._msgHistory[groupID].insert(0, msg)
                newMessages.insert(0, msg)

            return newMessages

