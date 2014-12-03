import unittest

from mock import patch
from tornwamp.messages import ERROR, PublishMessage, PUBLISH, PUBLISHED, SubscribeMessage, SUBSCRIBE, SUBSCRIBED
from tornwamp.processors.pubsub import PublishProcessor, SubscribeProcessor
from tornwamp.session import ClientConnection

#tornwamp.processors.pubsub                25      9      4      2    62%   44-60
#tornwamp.processors.pubsub.customize      18      9      2      2    45%   16, 41-56


class SubscribeProcessorTestCase(unittest.TestCase):

    def test_succeed(self):
        message = SubscribeMessage(request_id=123, topic="olympic.games")
        connection = ClientConnection(None)
        processor = SubscribeProcessor(message, connection)
        answer = processor.answer_message
        self.assertEqual(answer.code, SUBSCRIBED)
        self.assertEqual(answer.request_id, 123)

    @patch("tornwamp.processors.pubsub.customize.authorize_subscription", return_value=(False, "Your problem"))
    def test_fail(self, mock_authorize):
        message = SubscribeMessage(request_id=234, topic="olympic.games")
        connection = ClientConnection(None)
        processor = SubscribeProcessor(message, connection)
        answer = processor.answer_message
        self.assertEqual(answer.code, ERROR)
        self.assertEqual(answer.request_id, 234)
        self.assertEqual(answer.request_code, SUBSCRIBE)
        self.assertEqual(answer.uri, "tornwamp.subscribe.unauthorized")


class PublishProcessorTestCase(unittest.TestCase):

    def test_succeed(self):
        message = PublishMessage(request_id=345, topic="world.cup")
        connection = ClientConnection(None)
        processor = PublishProcessor(message, connection)
        answer = processor.answer_message
        self.assertEqual(answer.code, PUBLISHED)
        self.assertEqual(answer.request_id, 345)

    @patch("tornwamp.processors.pubsub.customize.authorize_publication", return_value=(False, "Your problem"))
    def test_fail(self, mock_authorize):
        message = PublishMessage(request_id=456, topic="world.cup")
        connection = ClientConnection(None)
        processor = PublishProcessor(message, connection)
        answer = processor.answer_message
        self.assertEqual(answer.code, ERROR)
        self.assertEqual(answer.request_id, 456)
        self.assertEqual(answer.request_code, PUBLISH)
        self.assertEqual(answer.uri, "tornwamp.publish.unauthorized")
