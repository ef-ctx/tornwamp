"""
Implement Tornado WAMP Handler.
"""
from tornado.websocket import WebSocketHandler

from tornwamp import customize, session
from tornwamp.messages import AbortMessage, Message
from tornwamp.processors import UnhandledProcessor


SUBPROTOCOL = 'wamp.2.json'


def abort(handler, error_msg, details, reason='tornwamp.error.unauthorized'):
    """
    Used to abort a connection while the user is trying to establish it.
    """
    abort_message = AbortMessage(reason=reason)
    abort_message.error(error_msg, details)
    handler.write_message(abort_message.json)
    handler.close(1, error_msg)


def deliver_messages(items):
    """
    Receives a dictionary with {websocket, message} and writes the message into the websocket
    """
    for item in items:
        recipient = item["websocket"]
        recipient.write_message(item["message"].json)


class WAMPHandler(WebSocketHandler):
    """
    WAMP WebSocket Handler.
    """

    def __init__(self, *args, **kargs):
        self.connection = None
        super(WAMPHandler, self).__init__(*args, **kargs)

    def select_subprotocol(self, subprotocols):
        "Select WAMP 2 subprocotol"
        return SUBPROTOCOL

    def authorize(self):
        """
        Override for authorizing connection before the WebSocket is opened.
        Sample usage: analyze the request cookies.

        Return a tuple containing:
        - boolean (if connection was accepted or not)
        - dict (containing details of the authentication)
        - string (explaining why the connection was not accepted)
        """
        return True, {}, ""

    def register_connection(self):
        """
        Add connection to connection's manager.
        """
        session.connections[self.connection.id] = self.connection

    def deregister_connection(self):
        """
        Remove connection from connection's manager.
        """
        return session.connections.pop(self.connection.id, None) if self.connection else None

    def open(self):
        """
        Responsible for authorizing or aborting WebSocket connection.
        It calls 'authorize' method and, based on its response, sends
        a ABORT message to the client.
        """
        authorized, details, error_msg = self.authorize()
        if authorized:
            self.connection = session.ClientConnection(self, **details)
            self.register_connection()
        else:
            abort(self, error_msg, details)

    def on_message(self, txt):
        """
        Handle incoming messages on the WebSocket. Each message will be parsed
        and handled by a Processor, which can be (re)defined by the user
        changing the value of 'processors' dict, available at
        tornwamp.customize module.
        """
        msg = Message.from_text(txt)
        Processor = customize.processors.get(msg.code, UnhandledProcessor)
        processor = Processor(msg, self.connection)

        if self.connection and not self.connection.zombie:  # TODO: cover branch else
            if processor.answer_message is not None:
                self.write_message(processor.answer_message.json)

        deliver_messages(processor.direct_messages)

        if processor.must_close:
            self.close(processor.close_code, processor.close_reason)

    def close(self, code=None, reason=None):
        """
        Invoked when a WebSocket is closed.
        """
        self.deregister_connection()
        super(WAMPHandler, self).close(code, reason)
