import unittest

from tornwamp import topic
from tornwamp.messages import EVENT, SubscribeMessage, PublishMessage
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
        items = customize.get_publish_direct_messages(msg, pub_id)
        self.assertEqual(len(items), 1)
        user_id = items[0]["connection"].user_id
        message = items[0]["message"]
        self.assertEqual(user_id, 7471)
        self.assertEqual(message.code, EVENT)
        self.assertEqual(message.subscription_id, 18273)
        self.assertEqual(message.publication_id, 91537)
        self.assertEqual(message.kwargs, {"type": "someMessage"})

    def test_get_subscribe_direct_messages(self):
        msg = SubscribeMessage(request_id=9581, topic="dolphins.are.non.human.people")
        subscription_id = 637
        items = customize.get_subscribe_direct_messages(msg, subscription_id)
        self.assertEqual(items, [])
