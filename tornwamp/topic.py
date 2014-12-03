"""
Used to handle PubSub topics publishers and subscribers
"""
from tornwamp.identifier import create_global_id


class TopicsManager(dict):
    """
    Manages all existing topics to which connections can potentially
    publish and/or subscribe to.
    """

    def add_subscriber(self, topic_name, connection, subscription_id=None):
        """
        Add a connection as a topic's subscriber.
        """
        topic = self.get(topic_name, Topic(topic_name))
        topic.subscribers.add(connection)
        self[topic_name] = topic
        subscription_id = subscription_id or create_global_id()
        connection.add_subscription_channel(subscription_id, topic_name)
        return subscription_id

    def remove_subscriber(self, topic_name, connection):
        """
        Remove a connection a topic's subscriber
        """
        topic = self.get(topic_name)
        if topic and connection in topic.subscribers:
            topic.subscribers.discard(connection)
            connection.remove_subscription_channel(topic_name)

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

    def remove_publisher(self, topic_name, connection):
        """
        Remove a connection a topic's subscriber
        """
        topic = self.get(topic_name)
        if topic and connection in topic.publishers:
            topic.publishers.discard(connection)
            connection.remove_publishing_channel(topic_name)

    def remove_connection(self, connection):
        """
        Connection is to be removed, scrap all connection publishers/subscribers in every topic
        """
        for topic_name in connection.get_publisher_topics():
            topic = self.get(topic_name)
            if topic:
                topic.publishers.discard(connection)

        for topic_name in connection.get_subscriber_topics():
            topic = self.get(topic_name)
            if topic:
                topic.subscribers.discard(connection)

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
