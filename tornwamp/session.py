"""
Abstract websocket connections (dual channel between clients and server).
"""
import socket
import errno

from datetime import datetime

from tornwamp import topic
from tornwamp.identifier import create_global_id


class ConnectionDict(dict):
    """
    Connections manager.
    """

    @property
    def dict(self):
        """
        Return a python dictionary which could be jsonified.
        """
        return {key: value.dict for key, value in self.items()}

    def filter_by_property_value(self, attr_name, attr_value):
        """
        Provided an attribute name and its value, retrieve connections which
        have it.
        """
        items = []
        for _, connection in self.items():
            if getattr(connection, attr_name) == attr_value:
                items.append(connection)
        return items


connections = ConnectionDict()


class ClientConnection(object):
    """
    Represent a client connection.
    """
    existing_ids = []

    def __init__(self, websocket, **details):
        """
        Create a connection object provided:
        - websocket (tornado.websocket.WebSocketHandler instance
        - details: dictionary of metadata associated to the connection
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
        self.topics = {
            "subscriber": {},
            "publisher": {}
        }

        # when connection should be closed but something is left
        self.zombie = False
        self.zombification_datetime = None

    @property
    def peer(self):
        try:
            ip, port = self._websocket.ws_connection.stream.socket.getpeername()
        except (AttributeError, OSError, socket.error) as error:
            if not hasattr(error, 'errno') or error.errno in (errno.EBADF, errno.ENOTCONN):
                # Expected errnos:
                #   - EBADF: bad file descriptor (connection was closed)
                #   - ENOTCONN: not connected (connection was never open)
                ip = self._websocket.request.remote_ip
                name = u"{0}:HACK|{1}".format(ip, self.id)
            else:
                # Rethrow exception in case of unknown errno
                raise
        else:
            forwarded_ip = self._websocket.request.headers.get("X-Forwarded-For")
            if forwarded_ip:
                ip = forwarded_ip
            name = u"{0}:{1}|{2}".format(ip, port, self.id)
        return name

    def get_subscription_id(self, topic_name):
        """
        Return connection's subscription_id for a specific topic.
        """
        subscribe_subscription = self.topics['subscriber'].get(topic_name)
        publish_subscription = self.topics['publisher'].get(topic_name)
        return subscribe_subscription or publish_subscription

    def add_subscription_channel(self, subscription_id, topic_name):
        """
        Add topic as a subscriber.
        """
        self.topics["subscriber"][topic_name] = subscription_id

    def remove_subscription_channel(self, topic_name):
        """
        Remove topic as a subscriber.
        """
        self.topics.get("subscriber", {}).pop(topic_name, None)

    def add_publishing_channel(self, subscription_id, topic_name):
        """
        Add topic as a publisher.
        """
        self.topics["publisher"][topic_name] = subscription_id

    def remove_publishing_channel(self, topic_name):
        """
        Remove topic as a publisher.
        """
        self.topics.get("publisher", {}).pop(topic_name, None)

    def get_publisher_topics(self):
        """
        Return list of topics to which this connection has subscribed.
        """
        return list(self.topics["publisher"])

    def get_topics(self):
        """
        Return a dictionary containing subscriptions_ids and connections - no
        matter if they are subscribers or publishers.
        """
        return dict(self.topics["subscriber"], **self.topics["publisher"])

    @property
    def topics_by_subscription_id(self):
        return {subscription_id: topic for topic, subscription_id in self.get_topics().items()}

    @property
    def dict(self):
        """
        Return dict representation of the current Connection, keeping only data
        that could be exported to JSON (convention: attributes which do not
        start with _).
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    def zombify(self):
        """
        Make current connection a zombie:
        - remove all its topics
        - remove it from the TopicsManager

        In WAMP, in order to disconnect, we're supposed to do a GOODBYE
        handshake.

        Considering the server wanted to disconnect the client for some reason,
        we leave the client in a "zombie" state, so it can't subscribe to
        topics and can't receive messages from other clients.
        """
        self.zombification_datetime = datetime.now().isoformat()
        self.zombie = True
        topic.topics.remove_connection(self)
