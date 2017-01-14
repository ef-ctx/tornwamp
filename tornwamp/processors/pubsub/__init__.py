""" WAMP-PubSub processors.
"""
from tornado import gen

from tornwamp.identifier import create_global_id
from tornwamp.messages import ErrorMessage, EventMessage, PublishMessage, PublishedMessage, SubscribeMessage, SubscribedMessage, BroadcastMessage
from tornwamp.processors import Processor
from tornwamp.processors.pubsub import customize
from tornwamp import topic as tornwamp_topic


class SubscribeProcessor(Processor):
    """
    Responsible for dealing SUBSCRIBE messages.
    """
    def process(self):
        """
        Return SUBSCRIBE message based on the input HELLO message.
        """
        received_message = SubscribeMessage(*self.message.value)
        allow, msg = customize.authorize_subscription(received_message.topic, self.connection)
        if allow:
            subscription_id = tornwamp_topic.topics.add_subscriber(
                received_message.topic,
                self.connection,
            )
            answer = SubscribedMessage(
                request_id=received_message.request_id,
                subscription_id=subscription_id
            )
            self.broadcast_messages = customize.get_subscribe_broadcast_messages(received_message, subscription_id, self.connection.id)
        else:
            answer = ErrorMessage(
                request_id=received_message.request_id,
                request_code=received_message.code,
                uri="tornwamp.subscribe.unauthorized"
            )
            answer.error(msg)
        self.answer_message = answer


class PublishProcessor(Processor):
    """
    Responsible for dealing SUBSCRIBE messages.
    """
    def process(self):
        """
        Return SUBSCRIBE message based on the input HELLO message.
        """
        received_message = PublishMessage(*self.message.value)
        allow, msg = customize.authorize_publication(received_message.topic, self.connection)
        answer = None
        if allow:
            publication_id = create_global_id()
            self.broadcast_messages, response = customize.get_publish_messages(received_message, publication_id, self.connection.id)
            if received_message.options.get("acknowledge"):
                if response is None:
                    answer = PublishedMessage(
                        request_id=received_message.request_id,
                        publication_id=publication_id
                    )
                else:
                    answer = response
        else:
            answer = ErrorMessage(
                request_id=received_message.request_id,
                request_code=received_message.code,
                uri="tornwamp.publish.unauthorized"
            )
            answer.error(msg)
        self.answer_message = answer
