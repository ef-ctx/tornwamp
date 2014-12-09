import unittest

from tornwamp import topic
from tornwamp.messages import Code, PublishMessage, SubscribeMessage
from tornwamp.processors.pubsub import customize
from tornwamp.session import ClientConnection
from tornwamp.topic import Topic


class CustomizeTestCase(unittest.TestCase):

    def setUp(self):
        topic_name = "education.first"
        self.original_topics = topic.topics
        connection = ClientConnection(None, user_id=7471)
        topic.topics.add_subscriber(topic_name, connection, 18273)

    def tearDown(self):
        topic.topics = self.original_topics

    def test_get_publish_direct_messages(self):
        msg = PublishMessage(request_id=168206, topic="education.first", kwargs={"type": "someMessage"})
        pub_id = 91537
        other_connection = ClientConnection(None, user_id=123)
        items = customize.get_publish_direct_messages(msg, pub_id, other_connection)
        self.assertEqual(len(items), 1)
        message = items[0]["message"]
        self.assertEqual(items[0]["websocket"], None)
        self.assertEqual(message.code, Code.EVENT)
        self.assertEqual(message.subscription_id, 18273)
        self.assertEqual(message.publication_id, 91537)
        self.assertEqual(message.kwargs, {"type": "someMessage"})

    def test_get_subscribe_direct_messages(self):
        msg = SubscribeMessage(request_id=9581, topic="dolphins.are.non.human.people")
        subscription_id = 637
        items = customize.get_subscribe_direct_messages(msg, subscription_id)
        self.assertEqual(items, [])
