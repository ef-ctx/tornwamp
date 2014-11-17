"""
"""
from datetime import datetime

from tornwamp.identifier import create_global_id


connections = {}


class ClientConnection(object):
    """
    Represent a client connection.
    """
    existing_ids = []

    def __init__(self, websocket, **details):
        """
        Create a connection object provided:
        - websocket (tornado.websocket.WebSocketHandler instance
        - details: dictionary of metadata associated to the connection. If it
        has 'channels' key, that will be used to subscribe to specific channels
        """
        self.id = create_global_id()

        # set connection attributes, if any is given
        for name, value in details.items():
            setattr(self, name, value)

        # meta-data
        # TODO: update this
        self.last_update = datetime.now().isoformat()

        # communication-related
        self._websocket = websocket
        self.zombie = False

        self.channels = []

#    @property
#    def dict(self):
#        """
#        Return dict representation of the current Connection, keeping only data
#        that could be exported to JSON (convention: attributes which do not
#        start with _).
#        """
#        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
#
#    def zombify(self):
#        """
#        Make current connection a zombie:
#        - remove it from all channels
#
#        In WAMP, in order to disconnect, we're supposed to do a GOODBYE
#        handshake.
#
#        Considering the server wanted to disconnect the client for some reason,
#        we leave the client in a "zombie" state, so it can't subscribe to
#        channels and can't receive messages from other clients.
#        """
#        self.zombification_datetime = datetime.now().isoformat()
#        self.channels = []
#        self.zombie = True
#        ChannelManager.remove_connection_from_all_channels(self)
