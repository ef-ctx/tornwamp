import mock

from tornadis import Client, PubSubClient
from tornado.ioloop import IOLoop
from tornado.testing import gen_test, AsyncTestCase

from tornwamp.messages import Message, EventMessage, BroadcastMessage
from tornwamp.topic import Topic, RedisUnavailableError


class TopicTestCase(AsyncTestCase):

    def setUp(self):
        super(TopicTestCase, self).setUp()
        self.topic = Topic(name="test", redis={"host": "127.0.0.1", "port": 6379})

    def test_create_connection(self):
        self.assertIsInstance(self.topic._publisher_connection, Client)
        self.assertFalse(self.topic._publisher_connection.is_connected())
        self.assertTrue(self.topic._publisher_connection.autoconnect)

    @gen_test
    def test_publish_message(self):
        # We use a dummy connection id as we are not testing local delivery
        msg = BroadcastMessage(
            "test",
            EventMessage(subscription_id="1", publication_id="1", kwargs={"type": "test"}),
            1,
        )
        client = PubSubClient(autoconnect=True, ioloop=IOLoop.current())
        yield client.pubsub_subscribe("test")
        ret = yield self.topic.publish(msg)
        self.assertTrue(ret)
        type_, topic, received_msg = yield client.pubsub_pop_message()
        self.assertEqual(type_.decode("utf-8"), u"message")
        self.assertEqual(topic.decode("utf-8"), u"test")
        received_msg = BroadcastMessage.from_text(received_msg.decode("utf-8"))
        self.assertEqual(received_msg.json, msg.json)

    @gen_test
    def test_redis_fails(self):
        with self.assertRaises(RedisUnavailableError):
            with mock.patch.object(self.topic._publisher_connection, "is_connected", return_value=False):
                msg = BroadcastMessage("test", EventMessage(subscription_id="1", publication_id="1"), 1)
                # We use a dummy connection id as we are not testing local delivery
                yield self.topic.publish(msg)
