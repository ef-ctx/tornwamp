"""
Processors are responsible for parsing received WAMP messages and providing
feedback to the server on what should be done (e.g. send answer message order
close connection).
"""
import abc
import six
from tornwamp.messages import Message, ErrorMessage, GoodbyeMessage, HelloMessage, WelcomeMessage


class Processor(six.with_metaclass(abc.ABCMeta)):
    """
    Abstract class which defines the base behavior for processing messages
    sent to the Websocket.

    Classes that extend this are supposed to overwride process method.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, message, connection):
        """
        msg: json
        session_id: string or number
        """
        self.session_id = getattr(connection, "id", None)
        self.connection = connection

        # message just received by the WebSocket
        self.message = message

        # messages to be sent by the WebSocket
        self.answer_message = None  # response message

        self.direct_messages = []  # to send direct messages to other connections
        # each item must have at least two keys: "connection" and "message"

        # the attributes below are in case we are expected to close the socket
        self.must_close = False
        self.close_code = None
        self.close_reason = None

        self.process()

    @abc.abstractmethod
    def process(self):
        """
        Responsible for processing the input message and may change the default
        values for the following attributes:
        - answer_message
        - broadcast_message
        - group_messages

        - must_close
        - close_code (1000 or in the range 3000 to 4999)
        - close_message
        """


class UnhandledProcessor(Processor):
    """
    Raises an error when the provided message can't be parsed
    """

    def process(self):
        message = Message(*self.message.value)
        description = "Unsupported message {0}".format(self.message.value)
        out_message = ErrorMessage(
            request_code=message.code,
            request_id=message.id,
            uri='wamp.unsupported.message'
        )
        out_message.error(description)
        self.answer_message = out_message


class HelloProcessor(Processor):
    """
    Responsible for dealing HELLO messages.
    """
    def process(self):
        """
        Return WELCOME message based on the input HELLO message.
        """
        # hello_message = HelloMessage(*self.message.value)
        # TODO: assert realm is in allowed list
        welcome_message = WelcomeMessage()
        self.answer_message = welcome_message


class GoodbyeProcessor(Processor):
    """
    Responsible for dealing GOODBYE messages.
    """
    def process(self):
        self.answer_message = GoodbyeMessage(*self.message.value)
        self.must_close = True
        # Excerpt from RFC6455 (The WebSocket Protocol)
        # "Endpoints MAY: use the following pre-defined status codes when sending
        # a Close frame:
        #   1000 indicates a normal closure, meaning that the purpose for
        #   which the connection was established has been fulfilled."
        # http://tools.ietf.org/html/rfc6455#section-7.4
        self.close_code = 1000
        self.close_reason = self.answer_message.details.get('message', '')
