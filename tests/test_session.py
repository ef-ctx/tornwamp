import unittest
from datetime import datetime

from mock import patch
from tornwamp.session import ClientConnection, ConnectionDict


class ClientConnectionTestCase(unittest.TestCase):

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
            "topics": [],
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
        self.assertEqual(connection.topics, [])
        self.assertTrue(connection.zombie)


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
                "topics": [],
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
