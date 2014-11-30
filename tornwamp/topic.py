"""
Used to handle PubSub topics publishers and subscribers
"""
from tornwamp.identifier import create_global_id


class TopicsManager(dict):
    """
    Manages all existing topics to which connections can potentially
    publish and/or subscribe to.
    """

    def add_subscriber(self, topic_name, connection):
        """
        Add a connection as a topic's subscriber.
        """
        topic = self.get(topic_name, Topic(topic_name))
        topic.subscribers.add(connection)
        self[topic_name] = topic
        subscription_id = create_global_id()
        connection.add_subscription_channel(subscription_id, topic_name)
        return subscription_id

    def add_publisher(self, topic_name, connection):
        """
        Add a connection as a topic's publisher.
        """
        topic = self.get(topic_name, Topic(topic_name))
        topic.publishers.add(connection)
        self[topic_name] = topic
        subscription_id = create_global_id()
        connection.add_publishing_channel(subscription_id, topic_name)
        return subscription_id

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
    def __init__(self, name):
        self.name = name
        self.subscribers = set()
        self.publishers = set()

    @property
    def dict(self):
        """
        Return a dict that is jsonifiable.
        """
        subscribers = [c.dict for c in self.subscribers]
        publishers = [c.dict for c in self.publishers]
        data = {
            "name": self.name,
            "subscribers": subscribers,
            "publishers": publishers
        }
        return data
