# GrouP2P
GrouP2P is a Python module that provides developers the ability to use GroupMe as a communication protocol rather than using a self-owned server or a premium hosting service.


### Why GrouP2P?

GrouP2P is not the only method of establishing user connections, as techniques like hole-punching exist. The key difference between GrouP2P and hole-punching, however, is that hole-punching may require end users to tweak their router configuration. This is not intuitive for the average consumer, so GrouP2P aims to circumvent that by using simple HTTP requests to send and receive data.

The GrouP2P class is the top-level class that can be solely used to interact with GroupMe. The basic features, such as creating, deleting, or joining groups, are available from a function call. Also included are a listener for new messages and a message sender. 

GrouP2P was designed to be a foundation for developers to build from, so the GroupMeAPI class allows developers to streamline the process of making HTTP requests to additional GroupMe API functions.

### Usage

To begin using GrouP2P, use the following command to install the package:

```console
pip install group2p
```
Once installed, importing "group2p" into your code will give you access to the complete module.

The GrouP2P class contains all of the top-level functions needed to interact with the GroupMe API. Initializing the object with a string containing your developer token will begin an attempt to establish a connection to the server under the user ID associated with the token. This can be accessed by the "userID" property.

## Config

The CONFIG_FILENAME file accessed by the "config" property and manipulated by the set_config() and get_config() functions.

set_config() takes an option as a string to be used for the key and any type for the value.

get_config() takes an option as a string to be used as the key to access a particular value in the JSON.

### Example

```python

```
