"""
This module should be overwride subscription procedures:
- authorize: if we will allow a connection to subscribe to a topic or not
- register: what we expect to happen (e.g. connection becomes a subscriber or
publisher of that topic)
"""
from tornwamp.topic import topics


def authorize(subscribe_message, connection):
    """
    Says if a user can allow or not.
    Return: True or False and the error message - if any.
    """
    return True, ""


def register(topic, connection):
    """
    By default, the connection is added as a subscriber of that topic.
    Return subscription ID.
    """
    subscription_id = topics.add_subscriber(topic, connection)
    return subscription_id
