import unittest

from mock import patch
from tornwamp.topic import Topic, TopicsManager
from tornwamp.session import ClientConnection


class MockSubscriber(object):
    dict = {"author": "plato"}


class TopicTestCase(unittest.TestCase):

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
