import socket
import unittest
from datetime import datetime

from mock import patch, MagicMock
from tornwamp.session import ClientConnection, ConnectionDict


class ClientConnectionTestCase(unittest.TestCase):

    def test_peer_on_not_connected_socket(self):
        ws = MagicMock()
        ws.ws_connection.stream.socket = socket.socket()
        ws.request.remote_ip = "127.0.0.1"
        client = ClientConnection(ws)
        client.id = 42
        self.assertEqual(client.peer, "127.0.0.1:HACK|42")

    def test_peer_on_closed_socket(self):
        ws = MagicMock()
        ws.ws_connection.stream.socket = socket.socket()
        ws.ws_connection.stream.socket.close()
        ws.request.remote_ip = "127.0.0.1"
        client = ClientConnection(ws)
        client.id = 42
        self.assertEqual(client.peer, "127.0.0.1:HACK|42")

    @patch("tornwamp.session.datetime")
    @patch("tornwamp.session.create_global_id", return_value=1111)
    def test_client_connection_with_details(self, mock_global_id, mock_datetime):
        mock_datetime.now.return_value = datetime(1984, 5, 11)
        connection = ClientConnection(websocket=None, user_name="Alex", speaks_chinese=True)
        self.assertEqual(connection.user_name, "Alex")
        self.assertTrue(connection.speaks_chinese)
        expected_response = {
            "user_name": "Alex",
            "speaks_chinese": True,
            "id": 1111,
            "topics": {'subscriber': {}, 'publisher': {}},
            "zombie": False,
            'zombification_datetime': None,
            "last_update": '1984-05-11T00:00:00'
        }
        self.assertEqual(connection.dict, expected_response)

    @patch("tornwamp.session.datetime")
    def test_connection_zombify(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2002, 4, 4)
        connection = ClientConnection(websocket=None)
        self.assertFalse(connection.zombie)
        connection.zombify()
        self.assertEqual(connection.zombification_datetime, '2002-04-04T00:00:00')
        self.assertEqual(connection.topics, {'subscriber': {}, 'publisher': {}})
        self.assertTrue(connection.zombie)

    def test_add_subscription_channel(self):
        connection = ClientConnection(websocket=None)
        connection.add_subscription_channel(7, "start.wars")
        expected_topics = {
            "subscriber": {
                "start.wars": 7
            },
            'publisher': {}
        }
        self.assertEqual(connection.topics, expected_topics)

    def test_get_publisher_topics(self):
        connection = ClientConnection(websocket=None)
        connection.add_subscription_channel(12, "again.do.nothing")
        connection.add_subscription_channel(32, "start.wars")
        expected_topics = ["again.do.nothing", "start.wars"]
        topics = connection.get_subscriber_topics()
        self.assertEqual(sorted(topics), expected_topics)

    def test_get_subscription_id(self):
        connection = ClientConnection(websocket=None)
        connection.add_subscription_channel(5, "a.new.hope")
        connection.add_subscription_channel(6, "the.empire.strikes.back")
        subscription_id = connection.get_subscription_id("a.new.hope")
        self.assertEqual(subscription_id, 5)

    def test_add_publishing_channel(self):
        connection = ClientConnection(websocket=None)
        connection.add_publishing_channel(42, "reason.for.life")
        expected_topics = {
            "publisher": {
                "reason.for.life": 42
            },
            'subscriber': {}
        }
        self.assertEqual(connection.topics, expected_topics)

    def test_get_publisher_topics(self):
        connection = ClientConnection(websocket=None)
        connection.add_publishing_channel(11, "dont.try.anything")
        connection.add_publishing_channel(42, "reason.for.life")
        expected_topics = ["dont.try.anything", "reason.for.life"]
        topics = connection.get_publisher_topics()
        self.assertEqual(sorted(topics), expected_topics)

    def test_get_topics(self):
        connection = ClientConnection(websocket=None)
        connection.add_subscription_channel(12, "whiplash")
        connection.add_publishing_channel(21, "reload")
        topics = connection.get_topics()
        expected_topics = {'reload': 21, 'whiplash': 12}
        self.assertEqual(topics, expected_topics)


class ConnectionDicttestCase(unittest.TestCase):

    @patch("tornwamp.session.datetime")
    @patch("tornwamp.session.create_global_id", return_value=2222)
    def test_connection_dict(self, mock_global_id, mock_datetime):
        mock_datetime.now.return_value = datetime(1950, 4, 6)
        connections = ConnectionDict()
        connections[2222] = ClientConnection(websocket=None, include=1, _exclude=True)
        expected_response = {
            2222: {
                "include": 1,
                "id": 2222,
                "topics": {'subscriber': {}, 'publisher': {}},
                "zombie": False,
                'zombification_datetime': None,
                "last_update": '1950-04-06T00:00:00'
            }
        }
        self.assertEqual(connections.dict, expected_response)

    def test_filter_by_property_value(self):
        connections = ConnectionDict()
        connections[1] = ClientConnection(websocket=None, name="Mario")
        connections[2] = ClientConnection(websocket=None, name="Goncalo")
        connections[3] = ClientConnection(websocket=None, name="Fredrik")
        answer = connections.filter_by_property_value("name", "Mario")
        self.assertEqual(answer, [connections[1]])
