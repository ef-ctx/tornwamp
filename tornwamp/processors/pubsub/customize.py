"""
This module should be overwride subscription procedures:
- authorize: if we will allow a connection to subscribe to a topic or not
- register: what we expect to happen (e.g. connection becomes a subscriber or
publisher of that topic)
"""


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


def get_subscribe_broadcast_message(received_message, subscription_id, connection_id):
    """
    Return a BroadcastMessage to be delivered to websocks, possibly connected
    through redis pub/sub
    """
    assert received_message is not None, "get_subscribe_broadcast_message requires a received_message"
    assert subscription_id is not None, "get_subscribe_broadcast_message requires a subscription_id"
    assert connection_id is not None, "get_subscribe_broadcast_message requires a connection_id"
