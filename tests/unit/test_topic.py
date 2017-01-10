import unittest

from mock import patch

from tornwamp import topic as tornwamp_topic
from tornwamp.messages import EventMessage, BroadcastMessage
from tornwamp.session import ClientConnection
from tornwamp.topic import Topic, TopicsManager


class MockSubscriber(object):
    dict = {"author": "plato"}


class TopicTestCase(unittest.TestCase):

    def setUp(self):
        self.old_customize = tornwamp_topic.customize

    def tearDown(self):
        tornwamp_topic.customize = self.old_customize

    def test_constructor(self):
        topic = Topic("the.monarchy")
        self.assertEqual(topic.name, "the.monarchy")
        self.assertEqual(topic.subscribers, {})
        self.assertEqual(topic.publishers, {})

    def test_dict(self):
        topic = Topic("the.republic")
        subscriber = MockSubscriber()
        topic.subscribers[123] = subscriber
        expected_dict = {
            'name': 'the.republic',
            'publishers': {},
            'subscribers': {
                123: {"author": "plato"}
            }
        }
        self.assertEqual(topic.dict, expected_dict)

    def test_connections(self):
        topic = Topic("start.trek")
        topic.subscribers = {1: 2}
        topic.publishers = {3: 4}
        expected = {1: 2, 3: 4}
        self.assertEqual(topic.connections, expected)

    def test_delivery_callback(self):
        msgs = []

        topic = Topic("another.topic")

        def f(t, msg, publisher_connection_id):
            self.assertEqual(publisher_connection_id, 1)
            self.assertEqual(t, topic)
            msgs.append(msg.json)

        tornwamp_topic.customize.deliver_event_messages = f

        msg = BroadcastMessage("another.topic", EventMessage(subscription_id=1, publication_id=1), 1)

        topic.publish(msg)
        self.assertEqual(msgs, [msg.event_message.json])


class TopicsManagerTestCase(unittest.TestCase):

    maxDiff = None

    def test_add_subscriber(self):
        manager = TopicsManager()
        connection = ClientConnection(None, name="Dracula")
        manager.add_subscriber("romania", connection, 432)
        connection = manager["romania"].subscribers.pop(432)
        self.assertEqual(connection.name, "Dracula")
        self.assertTrue("romania" in connection.topics["subscriber"])

    def test_remove_subscriber(self):
        manager = TopicsManager()
        connection = ClientConnection(None, name="Dracula")
        manager.add_subscriber("romania", connection, 95)
        self.assertEqual(len(manager["romania"].subscribers), 1)
        self.assertTrue("romania" in connection.topics["subscriber"])
        manager.remove_subscriber("romania", 95)
        self.assertEqual(len(manager["romania"].subscribers), 0)
        self.assertFalse("romania" in connection.topics["subscriber"])

    def test_remove_subscriber_inexistent_connection(self):
        manager = TopicsManager()
        answer = manager.remove_subscriber("inexistent", None)
        self.assertIsNone(answer)

    def test_add_publisher(self):
        manager = TopicsManager()
        connection = ClientConnection(None, name="Frankenstein")
        manager.add_publisher("gernsheim", connection, 123)
        connection = manager["gernsheim"].publishers.pop(123)
        self.assertEqual(connection.name, "Frankenstein")
        self.assertTrue("gernsheim" in connection.topics["publisher"])

    def test_remove_publisher(self):
        manager = TopicsManager()
        connection = ClientConnection(None, name="Frankenstein")
        manager.add_publisher("gernsheim", connection, 123)
        self.assertEqual(len(manager["gernsheim"].publishers), 1)
        self.assertTrue("gernsheim" in connection.topics["publisher"])
        manager.remove_publisher("gernsheim", 123)
        self.assertEqual(len(manager["gernsheim"].publishers), 0)
        self.assertFalse("gernsheim" in connection.topics["publisher"])

    def test_remove_publisher_inexistent_connection(self):
        manager = TopicsManager()
        answer = manager.remove_publisher("inexistent", None)
        self.assertIsNone(answer)

    def test_remove_connection(self):
        manager = TopicsManager()
        connection = ClientConnection(None, name="Drakenstein")
        manager.add_publisher("gernsheim", connection)
        self.assertEqual(len(manager["gernsheim"].publishers), 1)
        self.assertTrue("gernsheim" in connection.topics["publisher"])
        manager.add_subscriber("romania", connection)
        self.assertEqual(len(manager["romania"].subscribers), 1)
        self.assertTrue("romania" in connection.topics["subscriber"])
        manager.remove_connection(connection)
        self.assertEqual(len(manager["romania"].subscribers), 0)
        self.assertEqual(len(manager["gernsheim"].publishers), 0)

    @patch("tornwamp.session.create_global_id", side_effect=[1, 2])
    @patch("tornwamp.topic.create_global_id", side_effect=[3, 4])
    def test_dict(self, mock_id, mock_id_2):
        manager = TopicsManager()
        mr_hyde = ClientConnection(None, name="Mr Hyde")
        mr_hyde.last_update = None
        dr_jekyll = ClientConnection(None, name="Dr Jekyll")
        dr_jekyll.last_update = None
        manager.add_subscriber("scotland", mr_hyde)
        manager.add_publisher("scotland", dr_jekyll)
        expected_dict = {
            'scotland': {
                'name': 'scotland',
                'publishers': {
                    4: {
                        'id': 2,
                        'last_update': None,
                        'name': 'Dr Jekyll',
                        'topics': {
                            'subscriber': {},
                            'publisher': {
                                'scotland': 4
                            }
                        },
                        'zombie': False,
                        'zombification_datetime': None
                    }
                },
                'subscribers': {
                    3: {
                        'id': 1,
                        'last_update': None,
                        'name': 'Mr Hyde',
                        'topics': {
                            'subscriber': {
                                'scotland': 3
                            },
                            'publisher': {}
                        },
                        'zombie': False,
                        'zombification_datetime': None
                    }
                }
            }
        }
        self.assertEqual(manager.dict, expected_dict)

    def test_get_connection(self):
        manager = TopicsManager()
        frodo = ClientConnection(None, name="Frodo")
        sam = ClientConnection(None, name="Sam")
        manager.add_subscriber("lord.of.the.rings", frodo, subscription_id=1)
        manager.add_publisher("lord.of.the.rings", sam, subscription_id=2)
        hopefully_frodo = manager.get_connection("lord.of.the.rings", 1)
        hopefully_sam = manager.get_connection("lord.of.the.rings", 2)
        self.assertEqual(frodo, hopefully_frodo)
        self.assertEqual(sam, hopefully_sam)


class CustomizeTestCase(unittest.TestCase):

    def setUp(self):
        topic_name = "education.first"
        self.original_topics = tornwamp_topic.topics
        self.subscriber_connection = ClientConnection(None, user_id=7471)
        tornwamp_topic.topics.add_subscriber(topic_name, self.subscriber_connection, 18273)
        self.topic = tornwamp_topic.topics.get(topic_name)

    def tearDown(self):
        tornwamp_topic.topics = self.original_topics

    def test_deliver_event_messages(self):
        connection = ClientConnection(None, user_id=7475)
        with patch.object(self.subscriber_connection, "_websocket") as ws:
            tornwamp_topic.customize.deliver_event_messages(self.topic, EventMessage(subscription_id=1, publication_id=1), connection.id)
            ws.write_message.assert_called_once_with(EventMessage(subscription_id=18273, publication_id=1).json)

    def test_deliver_event_messages_none_publisher_connection_id(self):
        connection = ClientConnection(None, user_id=7475)
        with patch.object(self.subscriber_connection, "_websocket") as ws:
            tornwamp_topic.customize.deliver_event_messages(self.topic, EventMessage(subscription_id=1, publication_id=1))
            ws.write_message.assert_called_once_with(EventMessage(subscription_id=18273, publication_id=1).json)

    def test_deliver_event_messages_by_publishing(self):
        connection = ClientConnection(None, user_id=7475)
        with patch.object(self.subscriber_connection, "_websocket") as ws:
            msg = BroadcastMessage("education.first", EventMessage(subscription_id=1, publication_id=1), connection.id)
            tornwamp_topic.topics.get("education.first").publish(msg)
            ws.write_message.assert_called_once_with(EventMessage(subscription_id=18273, publication_id=1).json)

    def test_deliver_event_messages_empty_topic(self):
        connection = ClientConnection(None, user_id=7475)
        with patch.object(self.subscriber_connection, "_websocket") as ws:
            tornwamp_topic.customize.deliver_event_messages(Topic("education.second"), EventMessage(subscription_id=1, publication_id=1), connection.id)
            self.assertFalse(ws.write_message.called)

    def test_skip_publisher(self):
        with patch.object(self.subscriber_connection, "_websocket") as ws:
            tornwamp_topic.customize.deliver_event_messages(self.topic, EventMessage(subscription_id=1837, publication_id=1), self.subscriber_connection.id)
            self.assertFalse(ws.write_message.called)
