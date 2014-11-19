import unittest

from tornwamp.session import ClientConnection


class SessionTestCase(unittest.TestCase):

    def test_client_connection_with_details(self):
        connection = ClientConnection(websocket=None, user_id=1, is_cool=True)
        self.assertEqual(connection.user_id, 1)
        self.assertTrue(connection.is_cool)
