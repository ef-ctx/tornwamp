import unittest
from datetime import datetime

from mock import patch
from tornwamp.session import ClientConnection, ConnectionDict


class SessionTestCase(unittest.TestCase):

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
            "channels": [],
            "zombie": False,
            "last_update": '1984-05-11T00:00:00'
        }
        self.assertEqual(connection.dict, expected_response)

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
                "channels": [],
                "zombie": False,
                "last_update": '1950-04-06T00:00:00'
            }
        }
        self.assertEqual(connections.dict, expected_response)
