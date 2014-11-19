import unittest

from tornwamp.messages import HelloMessage, ERROR, WELCOME
from tornwamp.processors import Processor, HelloProcessor, UnhandledProcessor


class MockConnection(object):
    id = 1


connection = MockConnection()


class ProcessorTestCase(unittest.TestCase):

    def test_base_processor(self):
        with self.assertRaises(TypeError) as error:
            processor = Processor()
        msg = str(error.exception)
        expected_msg = "Can't instantiate abstract class Processor with abstract methods process"
        self.assertEqual(msg, expected_msg)

    def test_unhandled_processor(self):
        message = [456, 34, 'wamp.undefined.message']
        processor = UnhandledProcessor(message, connection)
        details = "Unsupported message [456, 34, 'wamp.undefined.message']"
        response = processor.answer_message
        self.assertEqual(response.code, ERROR)
        self.assertEqual(response.details["message"], details)
        self.assertEqual(response.uri, "wamp.unsupported.message")
        self.assertEqual(processor.must_close, False)

    def test_hello_processor(self):
        message = HelloMessage(realm="earth")
        processor = HelloProcessor(message, connection)
        response = processor.answer_message
        self.assertEqual(response.code, WELCOME)
