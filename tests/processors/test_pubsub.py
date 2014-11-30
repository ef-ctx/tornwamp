import unittest

from mock import patch
from tornwamp.messages import ERROR, SubscribeMessage, SUBSCRIBE, SUBSCRIBED
from tornwamp.processors.pubsub import SubscribeProcessor
from tornwamp.session import ClientConnection


class SubscribeProcessorTestCase(unittest.TestCase):

    def test_succeed(self):
        message = SubscribeMessage(request_id=123, topic="olympic.games")
        connection = ClientConnection(None)
        processor = SubscribeProcessor(message, connection)
        answer = processor.answer_message
        self.assertEqual(answer.code, SUBSCRIBED)
        self.assertEqual(answer.request_id, 123)

    @patch("tornwamp.processors.pubsub.customize.authorize", return_value=(False, "Your problem"))
    def test_fail(self, mock_authorize):
        message = SubscribeMessage(request_id=123, topic="olympic.games")
        connection = ClientConnection(None)
        processor = SubscribeProcessor(message, connection)
        answer = processor.answer_message
        self.assertEqual(answer.code, ERROR)
        self.assertEqual(answer.request_id, 123)
        self.assertEqual(answer.request_code, SUBSCRIBE)
        self.assertEqual(answer.uri, "tornwamp.subscribe.unauthorized")
