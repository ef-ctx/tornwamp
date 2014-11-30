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
        self.assertEqual(topic.subscribers, set())
        self.assertEqual(topic.publishers, set())

    def test_dict(self):
        topic = Topic("the.republic")
        subscriber = MockSubscriber()
        topic.subscribers.add(subscriber)
        expected_dict = {
            'name': 'the.republic',
            'publishers': [],
            'subscribers': [
                {"author": "plato"}
            ]
        }
        self.assertEqual(topic.dict, expected_dict)


class TopicsManagerTestCase(unittest.TestCase):

    maxDiff = None

    def test_add_subscriber(self):
        manager = TopicsManager()
        connection = ClientConnection(None, name="Dracula")
        manager.add_subscriber("romania", connection)
        connection = manager["romania"].subscribers.pop()
        self.assertEqual(connection.name, "Dracula")
        self.assertTrue("romania" in connection.topics["subscriber"].values())

    def test_add_publisher(self):
        manager = TopicsManager()
        connection = ClientConnection(None, name="Frankenstein")
        manager.add_publisher("gernsheim", connection)
        connection = manager["gernsheim"].publishers.pop()
        self.assertEqual(connection.name, "Frankenstein")
        self.assertTrue("gernsheim" in connection.topics["publisher"].values())

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
                'publishers': [
                    {
                        'id': 2,
                        'last_update': None,
                        'name': 'Dr Jekyll',
                        'topics': {
                            'publisher': {
                                4: 'scotland'
                            }
                        },
                        'zombie': False,
                        'zombification_datetime': None
                    }
                ],
                'subscribers': [
                    {
                        'id': 1,
                        'last_update': None,
                        'name': 'Mr Hyde',
                        'topics': {
                            'subscriber': {
                                3: 'scotland'
                            }
                        },
                        'zombie': False,
                        'zombification_datetime': None
                    }
                ]
            }
        }
        self.assertEqual(manager.dict, expected_dict)
