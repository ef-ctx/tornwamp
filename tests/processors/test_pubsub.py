import unittest
from mock import patch

from tornwamp.messages import Code, PublishMessage, SubscribeMessage
from tornwamp.processors.pubsub import PublishProcessor, SubscribeProcessor
from tornwamp.session import ClientConnection


class SubscribeProcessorTestCase(unittest.TestCase):

    def test_succeed(self):
        message = SubscribeMessage(request_id=123, topic="olympic.games")
        connection = ClientConnection(None)
        processor = SubscribeProcessor(message, connection)
        answer = processor.answer_message
        self.assertEqual(answer.code, Code.SUBSCRIBED)
        self.assertEqual(answer.request_id, 123)

    @patch("tornwamp.processors.pubsub.customize.authorize_subscription", return_value=(False, "Your problem"))
    def test_fail(self, mock_authorize):
        message = SubscribeMessage(request_id=234, topic="olympic.games")
        connection = ClientConnection(None)
        processor = SubscribeProcessor(message, connection)
        answer = processor.answer_message
        self.assertEqual(answer.code, Code.ERROR)
        self.assertEqual(answer.request_id, 234)
        self.assertEqual(answer.request_code, Code.SUBSCRIBE)
        self.assertEqual(answer.uri, "tornwamp.subscribe.unauthorized")


class PublishProcessorTestCase(unittest.TestCase):

    def test_succeed_without_acknowledge(self):
        message = PublishMessage(request_id=345, topic="world.cup")
        connection = ClientConnection(None)
        processor = PublishProcessor(message, connection)
        answer = processor.answer_message
        self.assertEqual(answer, None)

    def test_succeed_with_acknowledge(self):
        options = {"acknowledge": True}
        message = PublishMessage(request_id=345, topic="world.cup", options=options)
        connection = ClientConnection(None)
        processor = PublishProcessor(message, connection)
        answer = processor.answer_message
        self.assertEqual(answer.code, Code.PUBLISHED)
        self.assertEqual(answer.request_id, 345)

    @patch("tornwamp.processors.pubsub.customize.authorize_publication", return_value=(False, "Your problem"))
    def test_fail(self, mock_authorize):
        message = PublishMessage(request_id=456, topic="world.cup")
        connection = ClientConnection(None)
        processor = PublishProcessor(message, connection)
        answer = processor.answer_message
        self.assertEqual(answer.code, Code.ERROR)
        self.assertEqual(answer.request_id, 456)
        self.assertEqual(answer.request_code, Code.PUBLISH)
        self.assertEqual(answer.uri, "tornwamp.publish.unauthorized")
