"""
WAMP messages definitions and serializers.

Compatible with WAMP Document Revision: RC3, 2014/08/25, available at:
https://github.com/tavendo/WAMP/blob/master/spec/basic.md
"""

import json


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
    details = {}

    def __init__(self, code, *args):
        self.code = code
        self.value = [code] + list(args)

    @property
    def json(self):
        """
        Create a JSON representation of this message.
        """
        return json.dumps(self.value)

    def error(self, text):
        """
        Add error description. This is mainly useful for WAMP messages which
        have a details dictionary.
        """
        self.details["message"] = text


class HelloMessage(Message):
    """
    Sent by a Client to initiate opening of a WAMP session:
    [HELLO, Realm|uri, Details|dict]

    https://github.com/tavendo/WAMP/blob/master/spec/basic.md#hello
    """

    def __init__(self, code=HELLO, realm="", details=None):
        self.code = code
        self.realm = realm
        self.details = details if details else {}
        self.value = [self.code, self.realm, self.details]


class AbortMessage(Message):
    """
    Both the Router and the Client may abort the opening of a WAMP session
    [ABORT, Details|dict, Reason|uri]

    https://github.com/tavendo/WAMP/blob/master/spec/basic.md#abort
    """

    def __init__(self, code=ABORT, details=None, reason=None):
        assert not reason is None, "AbortMessage must have a reason"
        self.code = code
        self.details = details if details else {}
        self.reason = reason
        self.value = [self.code, self.details, self.reason]
