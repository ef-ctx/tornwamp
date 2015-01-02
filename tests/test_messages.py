import unittest

from tornwamp import messages as wamp
from tornwamp.messages import Code
from tornwamp.identifier import MIN_ID, MAX_ID


class MessageTestCase(unittest.TestCase):

    def test_base_message(self):
        raw = [Code.HELLO, "somerealm", {}]
        message = wamp.Message(*raw)
        self.assertEqual(message.code, Code.HELLO)
        self.assertEqual(message.value, raw)
        self.assertEqual(message.json, '[1, "somerealm", {}]')

    def test_message_without_id(self):
        raw = [201]
        message = wamp.Message(*raw)
        self.assertEqual(message.id, -1)

    def test_from_text(self):
        msg = wamp.Message.from_text("[1]")
        self.assertTrue(isinstance(msg, wamp.Message))
        msg = wamp.HelloMessage.from_text("[1]")
        self.assertTrue(isinstance(msg, wamp.HelloMessage))

    def test_error(self):
        msg = wamp.Message(34)
        msg.error("Some error", {"answer": 42})
        expected_details = {
            "message": "Some error",
            "details": {"answer": 42}
        }
        self.assertEqual(msg.details, expected_details)

    def test_hello_message(self):
        hello_message = wamp.HelloMessage(realm="world", details={"roles": {}})
        self.assertEqual(hello_message.code, Code.HELLO)
        self.assertEqual(hello_message.realm, "world")
        self.assertEqual(hello_message.details, {"roles": {}})
        self.assertEqual(hello_message.json, '[1, "world", {"roles": {}}]')

    def test_abort_message(self):
        abort_message = wamp.AbortMessage(reason="user.unauthorized")
        abort_message.error("Invalid cookie")
        self.assertEqual(abort_message.code, Code.ABORT)
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
        self.assertEqual(abort_message.code, Code.WELCOME)
        self.assertEqual(abort_message.details, wamp.DEFAULT_WELCOME_DETAILS)
        self.assertTrue(MIN_ID < abort_message.session_id < MAX_ID)

    def test_error_message_simple(self):
        error_message = wamp.ErrorMessage(
            request_code=2,
            request_id=3126,
            uri="some.very.buggy.error"
        )
        self.assertEqual(error_message.code, Code.ERROR)
        self.assertEqual(error_message.details, {})
        expected = [8, 2, 3126, {}, "some.very.buggy.error"]
        self.assertEqual(error_message.value, expected)

    def test_error_message_missing_request_code(self):
        with self.assertRaises(AssertionError) as error:
            abort_message = wamp.ErrorMessage()
        computed = str(error.exception)
        expected = "ErrorMessage must have request_code"
        self.assertEqual(computed, expected)

    def test_error_message_kwargs_only(self):
        error_message = wamp.ErrorMessage(
            request_code=3,
            request_id=7432,
            uri="horrible.exception",
            kwargs={'a': 1}
        )
        self.assertEqual(error_message.code, Code.ERROR)
        self.assertEqual(error_message.details, {})
        expected = [8, 3, 7432, {}, "horrible.exception", [], {'a': 1}]
        self.assertEqual(error_message.value, expected)

    def test_error_message_args_only(self):
        error_message = wamp.ErrorMessage(
            request_code=4,
            request_id=8259,
            uri="light.bug",
            args=["banana"]
        )
        self.assertEqual(error_message.code, Code.ERROR)
        self.assertEqual(error_message.details, {})
        expected = [8, 4, 8259, {}, "light.bug", ["banana"]]
        self.assertEqual(error_message.value, expected)

    def test_result_message(self):
        result_message = wamp.ResultMessage(request_id=8259)
        self.assertEqual(result_message.code, Code.RESULT)
        self.assertEqual(result_message.details, {})
        self.assertEqual(result_message.args, [])
        self.assertEqual(result_message.kwargs, {})
        expected = [50, 8259, {}]
        self.assertEqual(result_message.value, expected)

    def test_unsubscribe_message(self):
        unsubscribe_message = wamp.UnsubscribeMessage(request_id=1409, subscription_id=2)
        self.assertEqual(unsubscribe_message.code, Code.UNSUBSCRIBE)
        self.assertEqual(unsubscribe_message.request_id, 1409)
        self.assertEqual(unsubscribe_message.subscription_id, 2)
        expected = [34, 1409, 2]
        self.assertEqual(unsubscribe_message.value, expected)

    def test_unsubscribed_message(self):
        unsubscribed_message = wamp.UnsubscribedMessage(request_id=723)
        self.assertEqual(unsubscribed_message.code, Code.UNSUBSCRIBED)
        self.assertEqual(unsubscribed_message.request_id, 723)
        expected = [35, 723]
        self.assertEqual(unsubscribed_message.value, expected)
