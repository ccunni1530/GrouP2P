import json
from .groupme import *
from os import path
from time import monotonic

CONFIG_FILENAME = "config.json"

class GrouP2P:
    """
    Primary handler for interactions between GroupMe and the app
    using the service. Makes all calls necessary to the API and
    receives responses.
    """
    _msgHistory = None
    _user = {
        "connection": None
    }
    
    def __init__(self, token:str=""):
        """
        Initializes a connection to the GroupMe API.

        :param token: (optional) The access token to be used.
        :type token: str
        """
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

    @property
    def config(self) -> dict:
        """
        The contents of the config JSON.

        :returns: The JSON converted to a dictionary.
        :rtype: dict
        """
        with open(CONFIG_FILENAME, "r") as f:
            return json.loads(f.read())
        
    @property
    def userID(self) -> str:
        """
        :returns: The user's ID.
        :rtype: str
        """
        return self._user["connection"].user

    def set_config(self, option: str, value) -> dict:
        """
        Sets a config option and writes it to file.

        :param option: The key to be used to access the setting.
        :type option: str
        :param value: The value of the setting.
        :type value: any
        :returns: The updated settings as a dictionary.
        :rtype: dict
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

        :param option: The key to be used to retrieve the value.
        :type option: str
        :returns: The option requested, or None if the option wasn't found.
        :rtype: any
        """
        try:
            with open(CONFIG_FILENAME, "r") as f:
                settings = json.loads(f.read())
                return settings[option]
        except KeyError:
            return None

    def get_share_token(self, groupID: str) -> str:
        """
        Gets the share token of the specified group

        :param groupID: The ID of the group to retrieve the token from
        :type groupID: str
        :returns: The share token for the group, or nothing should an error occur.
        :rtype: str
        """
        response = self._user["connection"].get(f"groups/{groupID}")
        if response.status_code == 200:
            url = response.json()["response"]["share_url"]
            segments = url.split("/")
            return segments[-1]
        else:
            return ""

    def create_group(self, name="GrouP2P", users=None, share=True) -> requests.Response:
        """
        Starts a chat with the passed userIDs added.

        :param name: (default="GrouP2P") The name of the group to be created.
        :type name: str
        :param users: (default=None) The users to be added to the group upon creation.
        :type users: iterable
        :param share: Whether or not a share token will be generated upon creation.
        :type share: bool
        :returns: The server response.
        :rtype: requests.Response
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

    def delete_group(self, groupID: str) -> requests.Response:
        """"
        Deletes the specified group (must be creator).

        :param groupID: The ID of the group to be deleted.
        :type groupID: str
        :returns: The server response.
        :rtype: requests.Response
        """
        with self._user["connection"] as c:
            return c.post(f"groups/{groupID}/destroy")

    def join_group(self, groupID: str, shareToken: str) -> requests.Response:
        """
        Join the user to the specified group using the provided
        share token. Fails if the share token is invalid.

        :param groupID: The ID of the group to join.
        :type groupID: str
        :param shareToken: The share token used to allow access into the group.
        :type shareToken: str
        :returns: The server response.
        :rtype: requests.Response
        """
        with self._user["connection"] as c:
            return c.post(f"groups/{groupID}/join/{shareToken}")

    def send(self, data: str, groupID: str) -> requests.Response:
        """
        Sends a message to the specified group containing the
        provided data.

        :param data: The text to be sent as the body of the message.
        :type data: str
        :param groupID: The ID of the group to send the message to.
        :type groupID: str
        :returns: The server response.
        :rtype: requests.Response
        """
        
        with self._user["connection"] as c:
            params = dict()
            params["source_guid"] = str(monotonic())[-5:]
            params["text"] = data
            r = c.post(f"/groups/{groupID}/messages", params)

        return r

    def receive(self, groupID: str, limit=20) -> requests.Response:
        """
        Checks the group for any new messages and updates the history
        stored. Gets up to and including the (limit)th most recent
        message since the last known message.

        :param groupID: The ID of the group to retrieve messages from.
        :type groupID: str
        :param limit: (default=20) The max number of messages to retrieve.
        :type limit: int
        :returns: A list of all new messages.
        :rtype: requests.Response
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