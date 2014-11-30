"""
WAMP-PubSub processors.
"""
from tornwamp.messages import ErrorMessage, SubscribeMessage, SubscribedMessage
from tornwamp.processors import Processor
from tornwamp.processors.pubsub import customize


class SubscribeProcessor(Processor):
    """
    Responsible for dealing SUBSCRIBE messages.
    """
    def process(self):
        """
        Return SUBSCRIBE message based on the input HELLO message.
        """
        received_message = SubscribeMessage(*self.message.value)
        allow, msg = customize.authorize(received_message, self.connection)
        if allow:
            new_id = customize.register(received_message.topic, self.connection)
            answer = SubscribedMessage(
                request_id=received_message.request_id,
                subscription_id=new_id
            )
        else:
            answer = ErrorMessage(
                request_id=received_message.request_id,
                request_code=received_message.code,
                uri="tornwamp.subscribe.unauthorized"
            )
            answer.error(msg)
        self.answer_message = answer
