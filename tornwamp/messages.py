"""
WAMP messages definitions and serializers.

Compatible with WAMP Document Revision: RC3, 2014/08/25, available at:
https://github.com/tavendo/WAMP/blob/master/spec/basic.md
"""
import json
from copy import deepcopy

from enum import IntEnum
from tornwamp.identifier import create_global_id


class Code(IntEnum):
    """
    Enum which represents currently supported WAMP messages.
    """
    HELLO = 1
    WELCOME = 2
    ABORT = 3
    # CHALLENGE = 4
    # AUTHENTICATE = 5
    GOODBYE = 6
    # HEARTBEAT = 7
    ERROR = 8
    PUBLISH = 16
    PUBLISHED = 17
    SUBSCRIBE = 32
    SUBSCRIBED = 33
    UNSUBSCRIBE = 34
    UNSUBSCRIBED = 35
    EVENT = 36
    CALL = 48
    # CANCEL = 49
    RESULT = 50
    # REGISTER = 64
    # REGISTERED = 65
    # UNREGISTER = 66
    # UNREGISTERED = 67
    # INVOCATION = 68
    # INTERRUPT = 69
    # YIELD = 70


class Message(object):
    """
    Represent any WAMP message.
    """
    details = {}

    def __init__(self, code, *data, **kdata):
        self.code = code
        self.value = [code] + list(data)
        self.args = kdata.get("args", [])
        self.kwargs = kdata.get("kwargs", {})

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
        message_value = deepcopy(self.value)
        # TODO: test
        for index, item in enumerate(message_value):
            if isinstance(item, Code):
                message_value[index] = item.value
        return json.dumps(message_value)

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
        raw[0] = Code(raw[0])  # make it an object of type Code
        return cls(*raw)

    def _update_args_and_kargs(self):
        """
        Append args and kwargs to message value, according to their existance
        or not.
        """
        if self.kwargs:
            self.value.append(self.args)
            self.value.append(self.kwargs)
        else:
            if self.args:
                self.value.append(self.args)


class HelloMessage(Message):
    """
    Sent by a Client to initiate opening of a WAMP session:
    [HELLO, Realm|uri, Details|dict]

    https://github.com/tavendo/WAMP/blob/master/spec/basic.md#hello
    """

    def __init__(self, code=Code.HELLO, realm="", details=None):
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

    def __init__(self, code=Code.ABORT, details=None, reason=None):
        assert reason is not None, "AbortMessage must have a reason"
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

    def __init__(self, code=Code.WELCOME, session_id=None, details=None):
        self.code = code
        self.session_id = session_id or create_global_id()
        self.details = details or DEFAULT_WELCOME_DETAILS
        self.value = [self.code, self.session_id, self.details]


class GoodbyeMessage(Message):
    """
    Both the Server and the Client may abort the opening of a WAMP session
    [ABORT, Details|dict, Reason|uri]
    """

    def __init__(self, code=Code.GOODBYE, details=None, reason=None):
        self.code = code
        self.details = details or {}
        self.reason = reason or ""
        self.value = [self.code, self.details, self.reason]


class ResultMessage(Message):
    """
    Result of a call as returned by Dealer to Caller.

    [RESULT, CALL.Request|id, Details|dict]
    [RESULT, CALL.Request|id, Details|dict, YIELD.Arguments|list]
    [RESULT, CALL.Request|id, Details|dict, YIELD.Arguments|list, YIELD.ArgumentsKw|dict]
    """

    def __init__(self, code=Code.RESULT, request_id=None, details=None, args=None, kwargs=None):
        assert request_id is not None, "ResultMessage must have request_id"
        self.code = code
        self.request_id = request_id
        self.details = details or {}
        self.args = args or []
        self.kwargs = kwargs or {}
        self.value = [
            self.code,
            self.request_id,
            self.details
        ]
        self._update_args_and_kargs()


class CallMessage(Message):
    """
    Call as originally issued by the Caller to the Dealer.

    [CALL, Request|id, Options|dict, Procedure|uri]
    [CALL, Request|id, Options|dict, Procedure|uri, Arguments|list]
    [CALL, Request|id, Options|dict, Procedure|uri, Arguments|list, ArgumentsKw|dict]
    """

    def __init__(self, code=Code.CALL, request_id=None, options=None, procedure=None, args=None, kwargs=None):
        assert request_id is not None, "CallMessage must have request_id"
        assert procedure is not None, "CallMessage must have procedure"
        self.code = code
        self.request_id = request_id
        self.options = options or {}
        self.procedure = procedure
        self.args = args or []
        self.kwargs = kwargs or {}
        self.value = [
            self.code,
            self.request_id,
            self.options,
            self.procedure,
        ]
        self._update_args_and_kargs()


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

    def __init__(self, code=Code.ERROR, request_code=None, request_id=None, details=None, uri=None, args=None, kwargs=None):
        assert request_code is not None, "ErrorMessage must have request_code"
        assert request_id is not None, "ErrorMessage must have request_id"
        assert uri is not None, "ErrorMessage must have uri"
        self.code = code
        self.request_code = request_code
        self.request_id = request_id
        self.details = details or {}
        self.uri = uri
        self.args = args or []
        self.kwargs = kwargs or {}
        self.value = [
            self.code,
            self.request_code,
            self.request_id,
            self.details,
            self.uri
        ]
        self._update_args_and_kargs()


class SubscribeMessage(Message):
    """
    A Subscriber communicates its interest in a topic to the Server by sending
    a SUBSCRIBE message:
    [SUBSCRIBE, Request|id, Options|dict, Topic|uri]
    """

    def __init__(self, code=Code.SUBSCRIBE, request_id=None, options=None, topic=None):
        assert request_id is not None, "SubscribeMessage must have request_id"
        assert topic is not None, "SubscribeMessage must have topic"
        self.code = code
        self.request_id = request_id
        self.options = options or {}
        self.topic = topic
        self.value = [self.code, self.request_id, self.options, self.topic]


class SubscribedMessage(Message):
    """
    If the Broker is able to fulfill and allow the subscription, it answers by
    sending a SUBSCRIBED message to the Subscriber:
    [SUBSCRIBED, SUBSCRIBE.Request|id, Subscription|id]
    """
    def __init__(self, code=Code.SUBSCRIBED, request_id=None, subscription_id=None):
        assert request_id is not None, "SubscribedMessage must have request_id"
        assert subscription_id is not None, "SubscribedMessage must have subscription_id"
        self.code = code
        self.request_id = request_id
        self.subscription_id = subscription_id
        self.value = [self.code, self.request_id, self.subscription_id]


class PublishMessage(Message):
    """
    Sent by a Publisher to a Broker to publish an event.

    [PUBLISH, Request|id, Options|dict, Topic|uri]
    [PUBLISH, Request|id, Options|dict, Topic|uri, Arguments|list]
    [PUBLISH, Request|id, Options|dict, Topic|uri, Arguments|list, ArgumentsKw|dict]
    """
    def __init__(self, code=Code.PUBLISH, request_id=None, options=None, topic=None, args=None, kwargs=None):
        assert request_id is not None, "PublishMessage must have request_id"
        assert topic is not None, "PublishMessage must have topic"
        self.code = code
        self.request_id = request_id
        self.options = options or {}
        self.topic = topic
        self.args = args or []
        self.kwargs = kwargs or {}
        self.value = [self.code, self.request_id, self.options, self.topic]
        self._update_args_and_kargs()


class PublishedMessage(Message):
    """
    Acknowledge sent by a Broker to a Publisher for acknowledged publications.

    [PUBLISHED, PUBLISH.Request|id, Publication|id]
    """
    def __init__(self, code=Code.PUBLISHED, request_id=None, publication_id=None):
        assert request_id is not None, "PublishedMessage must have request_id"
        assert publication_id is not None, "PublishedMessage must have publication_id"
        self.code = code
        self.request_id = request_id
        self.publication_id = publication_id
        self.value = [self.code, self.request_id, self.publication_id]


class EventMessage(Message):
    """
    Event dispatched by Broker to Subscribers for subscription the event was matching.

    [EVENT, SUBSCRIBED.Subscription|id, PUBLISHED.Publication|id, Details|dict]
    [EVENT, SUBSCRIBED.Subscription|id, PUBLISHED.Publication|id, Details|dict, PUBLISH.Arguments|list]
    [EVENT, SUBSCRIBED.Subscription|id, PUBLISHED.Publication|id, Details|dict, PUBLISH.Arguments|list, PUBLISH.ArgumentsKw|dict]
    """
    def __init__(self, code=Code.EVENT, subscription_id=None, publication_id=None, details=None, args=None, kwargs=None):
        assert subscription_id is not None, "EventMessage must have subscription_id"
        assert publication_id is not None, "EventMessage must have publication_id"
        self.code = code
        self.subscription_id = subscription_id
        self.publication_id = publication_id
        self.details = details or {}
        self.args = args or []
        self.kwargs = kwargs or {}
        self.value = [self.code, self.subscription_id, self.publication_id, self.details]
        self._update_args_and_kargs()


class UnsubscribeMessage(Message):
    """
    Unsubscribe request sent by a Subscriber to a Broker to unsubscribe a subscription.
    [UNSUBSCRIBE, Request|id, SUBSCRIBED.Subscription|id]
    """
    def __init__(self, code=Code.UNSUBSCRIBE, request_id=None, subscription_id=None):
        assert request_id is not None, "UnsubscribeMessage must have request_id"
        assert subscription_id is not None, "UnsubscribeMessage must have subscription_id"
        self.code = code
        self.request_id = request_id
        self.subscription_id = subscription_id
        self.value = [self.code, self.request_id, self.subscription_id]


class UnsubscribedMessage(Message):
    """
    Acknowledge sent by a Broker to a Subscriber to acknowledge unsubscription.
    [UNSUBSCRIBED, UNSUBSCRIBE.Request|id]
    """
    def __init__(self, code=Code.UNSUBSCRIBED, request_id=None):
        assert request_id is not None, "UnsubscribedMessage must have request_id"
        self.code = code
        self.request_id = request_id
        self.value = [self.code, self.request_id]


CODE_TO_CLASS = {
    Code.HELLO: HelloMessage,
    Code.WELCOME: WelcomeMessage,
    Code.ABORT: AbortMessage,
    # CHALLENGE = 4
    # AUTHENTICATE = 5
    Code.GOODBYE: GoodbyeMessage,
    # HEARTBEAT = 7
    Code.ERROR: ErrorMessage,
    Code.PUBLISH: PublishMessage,
    Code.PUBLISHED: PublishedMessage,
    Code.SUBSCRIBE: SubscribeMessage,
    Code.SUBSCRIBED: SubscribedMessage,
    Code.UNSUBSCRIBE: UnsubscribeMessage,
    Code.UNSUBSCRIBED: UnsubscribedMessage,
    Code.EVENT: EventMessage,
    Code.CALL: CallMessage,
    # CANCEL = 49
    Code.RESULT: ResultMessage
    # REGISTER = 64
    # REGISTERED = 65
    # UNREGISTER = 66
    # UNREGISTERED = 67
    # INVOCATION = 68
    # INTERRUPT = 69
    # YIELD = 70
}

ERROR_PRONE_CODES = [Code.CALL, Code.SUBSCRIBE, Code.UNSUBSCRIBE, Code.PUBLISH]


def build_error_message(in_message, uri, description):
    """
    Return ErrorMessage instance (*) provided:
    - incoming message which generated error
    - error uri
    - error description

    (*) If incoming message is not prone to ERROR message reponse, return None.
    """
    msg = Message.from_text(in_message)
    if msg.code in ERROR_PRONE_CODES:
        MsgClass = CODE_TO_CLASS[msg.code]
        msg = MsgClass.from_text(in_message)
        answer = ErrorMessage(
            request_code=msg.code,
            request_id=msg.request_id,
            uri=uri
        )
        answer.error(description)
        return answer.json
