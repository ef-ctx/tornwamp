import unittest

from tornwamp.messages import CallMessage, ResultMessage, Code
from tornwamp.processors.rpc import CallProcessor


class MockConnection(object):
    id = 1


connection = MockConnection()


class CallProcessorTestCase(unittest.TestCase):

    def test_call_processor_ping(self):
        message = CallMessage(request_id=918273, procedure="ping")
        processor = CallProcessor(message, connection)
        response = processor.answer_message
        self.assertEqual(response.code, Code.RESULT)
        self.assertEqual(response.request_id, 918273)
        self.assertEqual(response.args[0], "Ping response")

    def test_call_processor_unsupported_method(self):
        message = CallMessage(request_id=192837, procedure="abc")
        processor = CallProcessor(message, connection)
        response = processor.answer_message
        self.assertEqual(response.code, Code.ERROR)
        self.assertEqual(response.request_id, 192837)
        self.assertEqual(response.uri, 'wamp.rpc.unsupported.procedure')
        self.assertEqual(response.details["message"], "The procedure abc doesn't exist")
