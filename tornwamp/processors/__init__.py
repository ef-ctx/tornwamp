import abc
from tornwamp.messages import Message, ErrorMessage, WelcomeMessage


class Processor(object):
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

        # message just received by the WebSocket
        self.message = message

        # messages to be sent by the WebSocket
        self.answer_message = None  # response message
        self.broadcast_message = None  # to be sent to * clients connected
        self.group_messages = {}  # to be sent to specific groups of clients

        # the attributes below are in case we are expected to close the socket
        self.must_close = False
        self.close_code = None
        self.close_message = None

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
        - close_code
        - close_message
        """


class UnhandledProcessor(Processor):
    """
    Raises an error when the provided message can't be parsed
    """

    def process(self):
        message = Message(*self.message)
        description = "Unsupported message {0}".format(self.message)
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
        welcome_message = WelcomeMessage()
        self.answer_message = welcome_message
