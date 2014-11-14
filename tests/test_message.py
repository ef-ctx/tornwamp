import unittest

from tornwamp import messages as wamp
from tornwamp.identifier import MIN_ID, MAX_ID


class MessageTestCase(unittest.TestCase):

    def test_base_message(self):
        raw = [1, "somerealm", {}]
        message = wamp.Message(*raw)
        self.assertEqual(message.code, wamp.HELLO)
        self.assertEqual(message.value, raw)
        self.assertEqual(message.json, '[1, "somerealm", {}]')

    def test_hello_message(self):
        hello_message = wamp.HelloMessage(realm="world", details={"roles": {}})
        self.assertEqual(hello_message.code, wamp.HELLO)
        self.assertEqual(hello_message.realm, "world")
        self.assertEqual(hello_message.details, {"roles": {}})
        self.assertEqual(hello_message.json, '[1, "world", {"roles": {}}]')
