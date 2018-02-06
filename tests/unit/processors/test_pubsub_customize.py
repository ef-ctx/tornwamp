import mock
import unittest

from tornwamp import topic
from tornwamp.messages import Code, PublishMessage, SubscribeMessage, EventMessage
from tornwamp.processors.pubsub import customize
from tornwamp.session import ClientConnection
from tornwamp.topic import Topic


class CustomizeTestCase(unittest.TestCase):

    def setUp(self):
        topic_name = "education.first"
        self.original_topics = topic.topics
        self.subscriber_connection = ClientConnection(None, user_id=7471)
        topic.topics.add_subscriber(topic_name, self.subscriber_connection, 18273)

    def tearDown(self):
        topic.topics = self.original_topics

    def test_get_broadcast_messages(self):
        msg = SubscribeMessage(request_id=9581, topic="dolphins.are.non.human.people")
        self.assertFalse(customize.get_subscribe_broadcast_messages(msg, 637, 5))
