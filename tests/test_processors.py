import unittest

from tornwamp.messages import GoodbyeMessage, HelloMessage, Message, Code
from tornwamp.processors import Processor, GoodbyeProcessor, HelloProcessor,\
    UnhandledProcessor


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
        message = Message(*[456, 34, 'wamp.undefined.message'])
        processor = UnhandledProcessor(message, connection)
        details = "Unsupported message [456, 34, 'wamp.undefined.message']"
        response = processor.answer_message
        self.assertEqual(response.code, Code.ERROR)
        self.assertEqual(response.details["message"], details)
        self.assertEqual(response.uri, "wamp.unsupported.message")
        self.assertEqual(processor.must_close, False)

    def test_hello_processor(self):
        message = HelloMessage(realm="earth")
        processor = HelloProcessor(message, connection)
        response = processor.answer_message
        self.assertEqual(response.code, Code.WELCOME)

    def test_goodbye_processor(self):
        message = GoodbyeMessage(details={"message": "adios"}, reason="i.dont.like.you")
        processor = GoodbyeProcessor(message, connection)
        response = processor.answer_message
        self.assertEqual(response.code, Code.GOODBYE)
        self.assertEqual(response.details, {"message": "adios"})
        self.assertEqual(response.reason, "i.dont.like.you")
        self.assertTrue(processor.must_close)
        self.assertEqual(processor.close_code, 1000)
        self.assertEqual(processor.close_reason, "adios")
