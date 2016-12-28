"""
Used to handle PubSub topics publishers and subscribers
"""
from tornado import gen
from tornado.ioloop import IOLoop
import tornadis

from tornwamp.topic import customize
from tornwamp.identifier import create_global_id


class RedisUnavailableError(Exception):
    pass


class TopicsManager(dict):
    """
    Manages all existing topics to which connections can potentially
    publish and/or subscribe to.
    """

    def add_subscriber(self, topic_name, connection, subscription_id=None):
        """
        Add a connection as a topic's subscriber.
        """
        new_topic = Topic(topic_name)
        topic = self.get(topic_name, new_topic)
        subscription_id = subscription_id or create_global_id()
        topic.subscribers[subscription_id] = connection
        self[topic_name] = topic
        connection.add_subscription_channel(subscription_id, topic_name)
        return subscription_id

    def remove_subscriber(self, topic_name, subscription_id):
        """
        Remove a connection a topic's subscriber provided:
        - topic_name
        - subscription_id
        """
        topic = self.get(topic_name)
        if topic and subscription_id in topic.subscribers:
            connection = topic.subscribers.pop(subscription_id)
            connection.remove_subscription_channel(topic_name)

    def add_publisher(self, topic_name, connection, subscription_id=None):
        """
        Add a connection as a topic's publisher.
        """
        topic = self.get(topic_name, Topic(topic_name))
        subscription_id = subscription_id or create_global_id()
        topic.publishers[subscription_id] = connection
        self[topic_name] = topic
        connection.add_publishing_channel(subscription_id, topic_name)
        return subscription_id

    def remove_publisher(self, topic_name, subscription_id):
        """
        Remove a connection a topic's subscriber
        """
        topic = self.get(topic_name)
        if topic and subscription_id in topic.publishers:
            connection = topic.publishers.pop(subscription_id)
            connection.remove_publishing_channel(topic_name)

    def remove_connection(self, connection):
        """
        Connection is to be removed, scrap all connection publishers/subscribers in every topic
        """
        for topic_name, subscription_id in connection.topics.get("publisher", {}).items():
            topic = self.get(topic_name)
            topic.publishers.pop(subscription_id, None)

        for topic_name, subscription_id in connection.topics.get("subscriber", {}).items():
            topic = self.get(topic_name)
            topic.subscribers.pop(subscription_id, None)

    def get_connection(self, topic_name, subscription_id):
        """
        Get topic connection provided topic_name and subscription_id. Try to find
        it in subscribers, otherwise, fetches from publishers.
        Return None if it is not available in any.
        """
        topic = self[topic_name]
        return topic.subscribers.get(subscription_id) or topic.publishers.get(subscription_id)

    @property
    def dict(self):
        """
        Return a dict that is jsonifiable.
        """
        return {k: topic.dict for k, topic in self.items()}


topics = TopicsManager()


class Topic(object):
    """
    Represent a topic, containing its name, subscribers and publishers.
    """
    def __init__(self, name, redis=None):
        self.name = name
        self.subscribers = {}
        self.publishers = {}
        if redis is not None:
            self._publisher_connection = tornadis.Client(ioloop=IOLoop.current(), autoconnect=True, **redis)
        else:
            self._publisher_connection = None

    @property
    def connections(self):
        """
        Return a set of topic connections - no matter if they are subscribers or publishers.
        """
        # About merging two dictionaries without changing the original one:

        # first version:
        # dict(self.subscribers, **self.publishers)
        # but it doesn't work with Python 3.5 if keyword args aren't strings

        # cool fancy Python3.5 way:
        # {**self.subscribers, **self.publishers}

        # Python 2+3 boring compatible way:
        conns = self.subscribers.copy()
        conns.update(self.publishers)
        return conns

    @property
    def dict(self):
        """
        Return a dict that is jsonifiable.
        """
        subscribers = {subscription_id: conn.dict for subscription_id, conn in self.subscribers.items()}
        publishers = {subscription_id: conn.dict for subscription_id, conn in self.publishers.items()}
        data = {
            "name": self.name,
            "subscribers": subscribers,
            "publishers": publishers
        }
        return data

    @gen.coroutine
    def publish(self, broadcast_msg):
        """
        Publish event_msg to all subscribers. This method will publish to
        redis if redis is available. Otherwise, it will run locally and can
        be called without yield.

        The parameter publisher_connection_id is used to not publish the
        message back to the publisher.
        """
        event_msg = broadcast_msg.event_message
        customize.deliver_event_messages(self, event_msg, broadcast_msg.publisher_connection_id)
        if self._publisher_connection is not None:
            ret = yield self._publisher_connection.call("PUBLISH", self.name, broadcast_msg.json)
            if isinstance(ret, tornadis.ConnectionError):
                raise RedisUnavailableError(ret)
            raise gen.Return(ret)
