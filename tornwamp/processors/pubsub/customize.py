"""
This module should be overwride subscription procedures:
- authorize: if we will allow a connection to subscribe to a topic or not
- register: what we expect to happen (e.g. connection becomes a subscriber or
publisher of that topic)
"""
from tornwamp import topic as tornwamp_topic
from tornwamp.messages import EventMessage


def authorize_publication(topic_name, connection):
    """
    Says if a user can publish to a topic or not.
    Return: True or False and the error message ("" if no error occured).
    """
    return True, ""


def authorize_subscription(topic_name, connection):
    """
    Says if a user can subscribe to a topic or not.
    Return: True or False and the error message ("" if no error occured).
    """
    return True, ""


def add_subscriber(topic, connection):
    """
    By default, the connection is added as a subscriber of that topic.
    Return subscription ID.
    """
    subscription_id = tornwamp_topic.topics.add_subscriber(topic, connection)
    return subscription_id


def get_direct_messages(publish_message, publication_id):
    """
    Return a list of dictionaries containing lists of connections and what
    message they should receive.
    """
    data = []
    topic_name = publish_message.topic
    topic = tornwamp_topic.topics.get(topic_name)
    if topic:
        for connection in topic.subscribers:
            subscription_id = connection.topics['subscriber'][topic_name]
            event_message = EventMessage(
                subscription_id=subscription_id,
                publication_id=publication_id,
                args=publish_message.args,
                kwargs=publish_message.kwargs,
            )
            item = {
                "connection": connection,
                "message": event_message
            }
            data.append(item)
    return data
