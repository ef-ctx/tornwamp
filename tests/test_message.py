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

    def test_from_text(self):
        msg = wamp.Message.from_text("[1]")
        self.assertTrue(isinstance(msg, wamp.Message))
        msg = wamp.HelloMessage.from_text("[1]")
        self.assertTrue(isinstance(msg, wamp.HelloMessage))

    def test_hello_message(self):
        hello_message = wamp.HelloMessage(realm="world", details={"roles": {}})
        self.assertEqual(hello_message.code, wamp.HELLO)
        self.assertEqual(hello_message.realm, "world")
        self.assertEqual(hello_message.details, {"roles": {}})
        self.assertEqual(hello_message.json, '[1, "world", {"roles": {}}]')

    def test_abort_message(self):
        abort_message = wamp.AbortMessage(reason="user.unauthorized")
        abort_message.error("Invalid cookie")
        self.assertEqual(abort_message.code, wamp.ABORT)
        self.assertEqual(abort_message.details, {"message": "Invalid cookie"})
        self.assertEqual(abort_message.reason, "user.unauthorized")
        expected = '[3, {"message": "Invalid cookie"}, "user.unauthorized"]'
        self.assertEqual(abort_message.json, expected)

    def test_abort_message_without_reason(self):
        with self.assertRaises(AssertionError) as error:
            abort_message = wamp.AbortMessage()
        computed = str(error.exception)
        expected = "AbortMessage must have a reason"
        self.assertEqual(computed, expected)

    def test_welcome_message(self):
        abort_message = wamp.WelcomeMessage()
        self.assertEqual(abort_message.code, wamp.WELCOME)
        self.assertEqual(abort_message.details, wamp.DEFAULT_WELCOME_DETAILS)
        self.assertTrue(MIN_ID < abort_message.session_id < MAX_ID)
