"""
WAMP messages definitions and serializers.

Compatible with WAMP Document Revision: RC3, 2014/08/25, available at:
https://github.com/tavendo/WAMP/blob/master/spec/basic.md
"""

import json

from tornwamp.identifier import create_global_id

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

    @classmethod
    def from_text(cls, text):
        """
        Decode text to JSON and return a Message object accordingly.
        """
        raw = json.loads(text)
        return cls(*raw)


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


DEFAULT_WELCOME_DETAILS = {
    "authrole": "anonymous",
    "authmethod": "anonymous",
    "roles": {
        "broker": {
            "features": {
                "publisher_identification": True,
                "publisher_exclusion": True,
                "subscriber_blackwhite_listing": True
            }
        },
        "dealer": {
            "features": {
                "progressive_call_results": True,
                "caller_identification": True
            }
        }
    },
    "authid": "jiQHbkkOxD1EFI7mJ1JITy3K"
}


class WelcomeMessage(Message):
    """
    Sent from the server side to open a WAMP session.
    The WELCOME is a reply message to the Client's HELLO.

    [WELCOME, Session|id, Details|dict]

    https://github.com/tavendo/WAMP/blob/master/spec/basic.md#welcome
    """

    def __init__(self, code=WELCOME, session_id=None, details=None):
        self.code = code
        self.session_id = session_id or create_global_id()
        self.details = details or DEFAULT_WELCOME_DETAILS
        self.value = [self.code, self.session_id, self.details]
