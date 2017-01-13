import unittest
from mock import patch

from tornwamp.messages import Code, ErrorMessage, PublishMessage, SubscribeMessage
from tornwamp.processors.pubsub import PublishProcessor, SubscribeProcessor, customize
from tornwamp.session import ClientConnection


class SubscribeProcessorTestCase(unittest.TestCase):

    def test_succeed(self):
        message = SubscribeMessage(request_id=123, topic="olympic.games")
        connection = ClientConnection(None)
        processor = SubscribeProcessor(message, connection)
        answer = processor.answer_message
        self.assertEqual(answer.code, Code.SUBSCRIBED)
        self.assertIsInstance(answer.subscription_id, int)
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

    def setUp(self):
        super(PublishProcessorTestCase, self).setUp()
        self.old_publish_messages = customize.get_publish_messages

    def tearDown(self):
        super(PublishProcessorTestCase, self).tearDown()
        customize.get_publish_messages = self.old_publish_messages

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

    def test_use_customized_message_if_available(self):
        options = {"acknowledge": True}
        expected_answer = ErrorMessage(
            request_id=345,
            request_code=16,
            uri="something.is.wrong"
        )
        def error(*args, **kwargs):
            return None, expected_answer
        customize.get_publish_messages = error
        message = PublishMessage(request_id=345, topic="world.cup", options=options)
        connection = ClientConnection(None)
        processor = PublishProcessor(message, connection)
        answer = processor.answer_message
        self.assertEqual(answer, expected_answer)
