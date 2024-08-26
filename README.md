# GrouP2P
GrouP2P is a Python module that provides developers the ability to use GroupMe as a communication protocol rather than using a self-owned server or a premium hosting service.


## Why GrouP2P?

GrouP2P is not the only method of establishing user connections, as techniques like STUN, IGP, and hole-punching exist. Between these options, hole-punching is both the easiest to set up and the most common solution. Like hole-punching, GrouP2P aims to be a simple implementation that developers can make use of.

The key difference between GrouP2P and hole-punching, however, is that hole-punching may require end users to tweak their router configuration. This is not intuitive for the average person, so GrouP2P aims to circumvent that by using simple HTTP requests to send and receive data between users.

The GrouP2P class is the top-level class that can be solely used to interact with GroupMe. The basic features, such as creating, deleting, or joining groups, are available from a function call. Also included are a listener for new messages and a message sender. 

GrouP2P was designed to be a foundation for developers to build from, so the GroupMeAPI class allows developers to streamline the process of making HTTP requests to additional GroupMe API functions.

## Usage

### Installation

To begin using GrouP2P, use the following command to install the package:

```console
pip install group2p
```
Once installed, importing "group2p" into your code will give you access to the complete module.

### GrouP2P and GroupMe Classes

The GrouP2P class contains all of the top-level functions needed to interact with the GroupMe API. Initializing the object with a string containing your developer token will begin an attempt to establish a connection to the server under the user ID associated with the token. This can be accessed by the ```userID``` property.

The ```create_group()```, ```delete_group()```, ```join_group()```, and ```send()``` functions will return a response object from the Requests module, so accessing the contents of your response can be done by using the built-in JSON converter.

```python
responseObj = group2pHandler.send("This is a message.", someGroupID)
desiredContent = responseObj.json()["response"][someContent]
print(desiredContent)
group2pHandler.delete_group(someGroupID)
```

Creating and deleting groups can be done with ease, having no required parameters for their functions. ```create_group``` can optionally specify the name, a list of users to invite, and whether or not it should get a share token.

```python
responseObj = group2pHandler.create_group(name="My Group", users=myFriendsList, share=False)
doStuff()
group2pHandler.delete_group(responseObj["response"]["id"])
```

Joining a group requires that the group ID and the share token are specified, the latter being found either in the ```create_group()``` response object or from calling ```get_share_token()```.

```python
responseObj = handler1.create_group()
groupID = responseObj["response"]["id"]
shareToken = handler1.get_share_token(groupID)
handler2.join_group(groupID, shareToken)
```

The ```send()``` function will send a string to a specified group, while ```receive()``` will get the most recent messages since the last recorded message.

```python
group2pHandler.send("Is anyone there?", someGroupID)
newMessages = group2pHandler.receive(someGroupID, limit=someMsgLimit)
if len(newMessages) > 0:
    print(newMessages[0]["text"])
```

The GroupMe class is the backend for GrouP2P, and can be used for total control over the HTTP requests being made. Basic interactions are already covered in GrouP2P, so only complex usage of GroupMe would require direct calls from this class.

### Config

The ```CONFIG_FILENAME``` file is accessed by the ```config``` property and manipulated by the ```set_config()``` and ```get_config()``` functions.

```set_config()``` takes an option as a string to be used for the key and any type for the value.

```get_config()``` takes an option as a string to be used as the key to access a particular value in the JSON.

## Example

The following code can be used to create a new group and send a message. ```example_basic.py``` and ```example_game.py``` both expand on this to create full programs. Currently, the example game hasn't been fully tested, so there may be some issues.

```python
from group2p import group2p

handle = group2p.GrouP2P()
response = handle.create_group(name="GrouP2P test")
groupID = response.json()["response"]["id"]
handle.send("Hello World!", groupID)
```