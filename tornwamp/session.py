"""
Abstract websocket connections (dual channel between clients and server).
"""
from datetime import datetime

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
        self.topics = {}

        # when connection should be closed but something is left
        self.zombie = False
        self.zombification_datetime = None

    def add_subscription_channel(self, subscription_id, topic_name):
        """
        Add topic as a subscriber.
        """
        self.topics.setdefault("subscriber", {topic_name: subscription_id})

    def remove_subscription_channel(self, topic_name):
        """
        Remove topic as a subscriber.
        """
        topics = self.topics.get("subscriber")
        if topics:
            del topics[topic_name]

    def get_subscriber_topics(self):
        topics = []
        for topic_name in self.topics["subscriber"]:
            topics.append(topic_name)
        return topics

    def add_publishing_channel(self, subscription_id, topic_name):
        """
        Add topic as a publisher.
        """
        topics = self.topics.get("publisher", {})
        topics[topic_name] = subscription_id  # doing in this order to debug
        self.topics["publisher"] = topics

    def remove_publishing_channel(self, topic_name):
        """
       Rmove topic as a publisher.
        """
        topics = self.topics.get("publisher")
        if topics:
            del topics[topic_name]

    def get_publisher_topics(self):
        topics = []
        for topic_name in self.topics["publisher"]:
            topics.append(topic_name)
        return topics

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
        self.topics = []
        self.zombie = True
#        TopicsManager.remove_connection_from_all_topics(self)
