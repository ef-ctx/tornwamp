"""
WAMP messages definitions and serializers.
"""

import json

# WAMP codes
HELLO = 1
WELCOME = 2
ABORT = 3
CHALLENGE = 4
AUTHENTICATE = 5
GOODBYE = 6
HEARTBEAT = 7
ERROR = 8
PUBLISH = 16
PUBLISHED = 17
SUBSCRIBE = 32
SUBSCRIBED = 33
UNSUBSCRIBE = 34
UNSUBSCRIBED = 35
EVENT = 36
CALL = 48
CANCEL = 49
RESULT = 50
REGISTER = 64
REGISTERED = 65
UNREGISTER = 66
UNREGISTERED = 67
INVOCATION = 68
INTERRUPT = 69
YIELD = 70


class Message(object):
    """
    Represent any WAMP message.
    """
    def __init__(self, code, *args):
        self.code = code
        self.value = [code] + list(args)

    @property
    def json(self):
        """
        Create a JSON representation of this message.
        """
        return json.dumps(self.value)


class HelloMessage(Message):
    """
    Sent by a Client to initiate opening of a WAMP session:
    [HELLO, Realm|uri, Details|dict]
    """

    def __init__(self, code=HELLO, realm="", details=None):
        self.code = code
        self.realm = realm
        self.details = details if details else {}

    @property
    def value(self):
        """
        Define the structure to be used to generate a JSON WAMP-compatible.
        """
        return [self.code, self.realm, self.details]
