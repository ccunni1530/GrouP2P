# GrouP2P
GrouP2P is a Python module that provides developers the ability to use GroupMe as a communication protocol rather than using a self-owned server or a premium hosting service.


### Why GrouP2P?

GrouP2P is not the only method of establishing user connections, as techniques like hole-punching exist. The key difference between GrouP2P and hole-punching, however, is that hole-punching may require end users to tweak their router configuration. This is not intuitive for the average consumer, so GrouP2P aims to circumvent that by using simple HTTP requests to send and receive data.


### Usage

The GrouP2P class is the top-level class that can be solely used to interact with GroupMe. The basic features, such as creating, deleting, or joining groups, are available from a function call. Also included are a listener for new messages and a message sender. 

GrouP2P was designed to be a foundation for developers to build from, so the GroupMeAPI class allows developers to streamline the process of making HTTP requests to additional GroupMe API functions.


### Example

```python

```
