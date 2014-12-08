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
    assert topic_name, "authorize_publication requires topic_name"
    assert connection, "authorize_publication requires connection"
    return True, ""


def authorize_subscription(topic_name, connection):
    """
    Says if a user can subscribe to a topic or not.
    Return: True or False and the error message ("" if no error occured).
    """
    assert topic_name, "authorize_subscription requires topic_name"
    assert connection, "authorize_subscription requires connection"
    return True, ""


def add_subscriber(topic, connection):
    """
    By default, the connection is added as a subscriber of that topic.
    Return subscription ID.
    """
    subscription_id = tornwamp_topic.topics.add_subscriber(topic, connection)
    return subscription_id


def get_subscribe_direct_messages(subscribe_message, subscription_id):
    """
    Return a list of dictionaries containing websocket and what message they
    should receive. This is called from SubscribeProcessor when it succeeds.

    Sample response:
    [
        {
            "websocket": <tornwamp.WAMPHandler>,
            "message": <tornwamp.messages.Event>
        }
    ]
    """
    assert subscribe_message, "get_subscribe_direct_messages requires subscribe_message"
    assert subscription_id, "get_subscribe_direct_messages requires subscription_id"
    return []


def get_publish_direct_messages(publish_message, publication_id, publisher_connection):
    """
    Return a list of dictionaries containing websocket and what message they
    should receive. This is called from PublishProcessor when it succeeds.

    Sample response:
    [
        {
            "websocket": <tornwamp.WAMPHandler>,
            "message": <tornwamp.messages.Event>
        }
    """
    data = []
    topic_name = publish_message.topic
    topic = tornwamp_topic.topics.get(topic_name)
    if topic:
        for subscription_id, connection in topic.subscribers.items():
            if connection != publisher_connection:
                event_message = EventMessage(
                    subscription_id=subscription_id,
                    publication_id=publication_id,
                    args=publish_message.args,
                    kwargs=publish_message.kwargs,
                )
                item = {
                    "websocket": connection._websocket,
                    "message": event_message
                }
                data.append(item)
    return data
