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
    def id(self):
        """
        For all kinds of messages (except ERROR) that have [Request|id], it is
        in the second position of the array.
        """
        if (len(self.value) > 1) and isinstance(self.value[1], int):
            return self.value[1]
        return -1

    @property
    def json(self):
        """
        Create a JSON representation of this message.
        """
        return json.dumps(self.value)

    def error(self, text, info=None):
        """
        Add error description and aditional information.

        This is useful for ABORT and ERROR messages.
        """
        self.details["message"] = text
        if info:
            self.details["details"] = info

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
        self.details = details or {}
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


class ErrorMessage(Message):
    """
    Error reply sent by a Peer as an error response to different kinds of
    requests.

    [ERROR, REQUEST.Type|int, REQUEST.Request|id, Details|dict, Error|uri]
    [ERROR, REQUEST.Type|int, REQUEST.Request|id, Details|dict, Error|uri,
        Arguments|list]
    [ERROR, REQUEST.Type|int, REQUEST.Request|id, Details|dict, Error|uri,
        Arguments|list, ArgumentsKw|dict]
    """

    def __init__(self, code=ERROR, request_code=None, request_id=None, details=None, uri=None, args=None, kwargs=None):
        assert not request_code is None, "ErrorMessage must have request_code"
        assert not request_id is None, "ErrorMessage must have request_id"
        assert not uri is None, "ErrorMessage must have uri"
        self.code = code
        self.request_code = request_code
        self.request_id = request_id
        self.details = details or {}
        self.uri = uri
        self.args = args or []
        self.kwargs = kwargs or {}

    @property
    def value(self):
        data = [
            self.code,
            self.request_code,
            self.request_id,
            self.details,
            self.uri
        ]
        if self.kwargs:
            data.append(self.args)
            data.append(self.kwargs)
        else:
            if self.args:
                data.append(self.args)
        return data
