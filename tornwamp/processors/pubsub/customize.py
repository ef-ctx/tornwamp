"""
This module should be overwride subscription procedures:
- authorize_subscription: if we will allow a connection to subscribe to
  a topic or not
- authorize_publication: if we will allow a connection to publish to
  a topic or not
- get_subscribe_broadcast_messages: if we want to send broadcast
  messages when a client subscribes to a topic
- get_publish_message: if we want to customize the broadcast message
  when a client publishes to a topic. The response to the client can
  also be customized with that function.
"""
from tornwamp import messages


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


def get_subscribe_broadcast_messages(received_message, subscription_id, connection_id):
    """
    Return a BroadcastMessage to be delivered to other connections,
    possibly connected through redis pub/sub

    This message is called whenever an user subscribes to a topic.
    """
    assert received_message is not None, "get_subscribe_broadcast_message requires a received_message"
    assert subscription_id is not None, "get_subscribe_broadcast_message requires a subscription_id"
    assert connection_id is not None, "get_subscribe_broadcast_message requires a connection_id"
    return []


def get_publish_messages(received_message, publication_id, connection_id):
    """
    Return a tuple with two messages:
    (BroadcastMessage, PublishedMessage|ErrorMessage)
    - BroadcastMessage: message to be delivered to the subscribers
    - PublishedMessage|ErrorMessage: message to be returned to the publisher.

    If the second element of the tuple is None, then a default
    PublishedMessage will be returned to the publisher.

    This message is called whenever a message is published.
    """
    event_message = messages.EventMessage(
        publication_id=publication_id,
        args=received_message.args,
        kwargs=received_message.kwargs,
    )
    broadcast_msg = messages.BroadcastMessage(
        topic_name=received_message.topic,
        event_message=event_message,
        publisher_connection_id=connection_id,
    )
    return [broadcast_msg], None
