import unittest

from tornwamp import messages as wamp


class MessageTestCase(unittest.TestCase):

    def test_base_message(self):
        raw_data = [1, "somerealm", {}]
        message = wamp.Message(*raw_data)
        self.assertEqual(message.code, wamp.HELLO)
        self.assertEqual(message.value, raw_data)
        self.assertEqual(message.json, '[1, "somerealm", {}]')
