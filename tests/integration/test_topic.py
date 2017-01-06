import mock
import socket
import uuid
import time

from tornadis import Client, PubSubClient
from tornado.ioloop import IOLoop
from tornado.testing import gen_test, AsyncTestCase

from tornwamp import session
from tornwamp import handler
from tornwamp import topic
from tornwamp.messages import Message, EventMessage, BroadcastMessage
from tornwamp.topic import Topic, RedisUnavailableError


class TopicTestCase(AsyncTestCase):

    def setUp(self):
        super(TopicTestCase, self).setUp()
        self.topic = Topic(name="test", redis={"host": "127.0.0.1", "port": 6379})
        self.old_timeout = topic.PUBSUB_TIMEOUT
        topic.PUBSUB_TIMEOUT = 1

    def tearDown(self):
        topic.PUBSUB_TIMEOUT = self.old_timeout

    def wait_for(self, future):
        self.io_loop.add_future(future, lambda x: self.stop())
        return self.wait()

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
    def test_publish_redis_fails(self):
        with self.assertRaises(RedisUnavailableError):
            with mock.patch.object(self.topic._publisher_connection, "is_connected", return_value=False):
                msg = BroadcastMessage("test", EventMessage(subscription_id="1", publication_id="1"), 1)
                # We use a dummy connection id as we are not testing local delivery
                yield self.topic.publish(msg)

    def test_receive_message_from_other_node(self):
        handler_mock = mock.MagicMock()

        connection = session.ClientConnection(handler_mock)
        self.wait_for(self.topic.add_subscriber("7", connection))

        event_msg = EventMessage(subscription_id="1", publication_id="1", kwargs={"type": "test"})
        msg = BroadcastMessage("test", event_msg, 1)
        msg.publisher_node_id = uuid.uuid4().hex
        node2_topic = Topic(name="test", redis={"host": "127.0.0.1", "port": 6379})
        self.wait_for(node2_topic.publish(msg))

        # wait for all futures to execute
        self.io_loop.close()

        event_msg.subscription_id = "7"
        handler_mock.write_message.assert_called_once_with(event_msg.json)

    def test_receive_two_messages_from_other_node(self):
        handler_mock = mock.MagicMock()

        connection = session.ClientConnection(handler_mock)
        self.wait_for(self.topic.add_subscriber("7", connection))

        event_msg = EventMessage(subscription_id="1", publication_id="1", kwargs={"type": "test"})
        msg = BroadcastMessage("test", event_msg, 1)
        msg.publisher_node_id = uuid.uuid4().hex
        node2_topic = Topic(name="test", redis={"host": "127.0.0.1", "port": 6379})
        self.wait_for(node2_topic.publish(msg))

        event_msg.kwargs["type"] = "test2"
        self.wait_for(node2_topic.publish(msg))

        # wait for all futures to execute
        self.io_loop.close()

        event_msg.subscription_id = "7"
        expected_calls = [
            mock.call('[36, "7", "1", {}, [], {"type": "test"}]'),
            mock.call('[36, "7", "1", {}, [], {"type": "test2"}]')
        ]
        self.assertEqual(handler_mock.write_message.mock_calls, expected_calls)

    def test_receive_message_from_same_node(self):
        handler_mock = mock.MagicMock()

        connection = session.ClientConnection(handler_mock)
        self.wait_for(self.topic.add_subscriber("7", connection))

        event_msg = EventMessage(subscription_id="1", publication_id="1", kwargs={"type": "test"})
        msg = BroadcastMessage("test", event_msg, 1)
        self.wait_for(self.topic.publish(msg))

        # wait for all futures to execute
        self.io_loop.close()

        event_msg.subscription_id = "7"
        handler_mock.write_message.assert_called_once_with(event_msg.json)

    @gen_test
    def test_redis_fails_on_publish(self):
        event_msg = EventMessage(subscription_id="1", publication_id="1", kwargs={"type": "test"})
        msg = BroadcastMessage("test", event_msg, 1)
        with self.assertRaises(RedisUnavailableError):
            with mock.patch.object(self.topic._publisher_connection, "is_connected", return_value=False):
                yield self.topic.publish(msg)

    @gen_test
    def test_redis_fails_on_subscribe(self):
        connection = session.ClientConnection(mock.MagicMock())
        with self.assertRaises(RedisUnavailableError):
            with mock.patch("tornadis.PubSubClient.is_connected", return_value=False):
                yield self.topic.add_subscriber("7", connection)

    @gen_test
    def test_redis_fails_to_connect(self):
        connection = session.ClientConnection(mock.MagicMock())
        with self.assertRaises(RedisUnavailableError):
            with mock.patch("socket.socket.connect", side_effect=socket.error):
                yield self.topic.add_subscriber("7", connection)


    def test_pop_message_timeout(self):
        handler_mock = mock.MagicMock()

        connection = session.ClientConnection(handler_mock)
        self.wait_for(self.topic.add_subscriber("7", connection))

        time.sleep(1.5)

        event_msg = EventMessage(subscription_id="1", publication_id="1", kwargs={"type": "test"})
        msg = BroadcastMessage("test", event_msg, 1)
        msg.publisher_node_id = uuid.uuid4().hex
        self.wait_for(self.topic._publisher_connection.call("PUBLISH", self.topic.name, msg.json))

        # wait for all futures to execute
        self.io_loop.close()

        event_msg.subscription_id = "7"
        handler_mock.write_message.assert_called_once_with(event_msg.json)

    def test_pop_message_timeout_drop_subscribers(self):
        handler_mock = mock.MagicMock()

        connection = session.ClientConnection(handler_mock)
        self.wait_for(self.topic.add_subscriber("7", connection))

        self.topic._subscriber_connection = None

        time.sleep(1.5)

        # wait for all futures to execute
        self.wait_for(self.topic._publisher_connection.call("GET", "a"))
        self.io_loop.close()

        self.assertTrue(handler_mock.close.called)
        self.assertEqual(len(self.topic.subscribers), 0)

    def test_disconnect_redis_drop_subscribers(self):
        handler_mock = mock.MagicMock()

        connection = session.ClientConnection(handler_mock)
        self.wait_for(self.topic.add_subscriber("7", connection))

        self.topic._subscriber_connection.disconnect()

        # wait for all futures to execute
        self.wait_for(self.topic._publisher_connection.call("GET", "a"))
        self.io_loop.close()

        self.assertTrue(handler_mock.close.called)
        self.assertEqual(len(self.topic.subscribers), 0)
