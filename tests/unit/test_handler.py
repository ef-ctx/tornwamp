from mock import patch
from tornado.concurrent import Future
from tornado.httpclient import HTTPRequest
from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.web import Application
from tornado.websocket import websocket_connect

from tornwamp import messages, session, topic as tornwamp_topic
from tornwamp.handler import WAMPHandler
from tornwamp.processors.pubsub import customize as pubsub_customize
from tornwamp.processors import rpc


class MockWebsocket(object):
    message = None

    def write_message(self, msg):
        self.message = msg


class MockConnection(object):

    def __init__(self):
        self._websocket = MockWebsocket()
        self.id = 1

    def add_subscription_channel(self, *args):
        pass


class MockMessage(object):
    json = "mocked message"


class UnauthorizeWAMPHandler(WAMPHandler):

    def authorize(self):
        return False, {}, "Denied"


class WAMPHandlerTestCase(AsyncHTTPTestCase):

    def setUp(self):
        session.connections = {}
        self.old_procedures = rpc.customize.procedures
        rpc.customize.procedures = rpc.customize.procedures.copy()
        super(WAMPHandlerTestCase, self).setUp()

    def tearDown(self):
        rpc.customize.procedures = self.old_procedures

    def get_app(self):
        application = Application([
            (r"/ws", WAMPHandler),
            (r"/no", UnauthorizeWAMPHandler)
        ])
        return application

    def build_request(self, path="ws", headers=None):
        port = self.get_http_port()
        url = 'ws://0.0.0.0:{0}/{1}'.format(port, path)
        if not headers:
            headers = {}
        if 'Origin' not in headers:
            headers['Origin'] = 'http://0.0.0.0:%d' % port
        headers['Sec-WebSocket-Protocol'] = 'wamp.2.json'
        return HTTPRequest(url, headers=headers)

    @gen_test
    def test_connection_succeeds(self):
        request = self.build_request()
        ws = yield websocket_connect(request)
        msg = messages.HelloMessage(realm="burger.friday")
        ws.write_message(msg.json)

        response = yield ws.read_message()
        message = messages.Message.from_text(response)
        self.assertIs(message.code, messages.Code.WELCOME)
        self.assertFalse(getattr(ws, "close_code", False))
        ws.close()

    @gen_test
    def test_connection_with_xforwardedfor(self):
        request = self.build_request(headers={"X-Forwarded-For": "10.0.0.1"})
        ws = yield websocket_connect(request)
        msg = messages.HelloMessage(realm="burger.thursday")
        ws.write_message(msg.json)

        connection_ip = list(session.connections.values())[0]
        self.assertTrue(connection_ip.peer.startswith("10.0.0.1"))

        response = yield ws.read_message()
        message = messages.Message.from_text(response)
        self.assertIs(message.code, messages.Code.WELCOME)
        self.assertFalse(getattr(ws, "close_code", False))
        ws.close()

    @gen_test
    def test_authorization_fails(self):
        request = self.build_request(path="no")
        ws = yield websocket_connect(request)
        text = yield ws.read_message()

        message = messages.AbortMessage.from_text(text)
        self.assertIs(message.code, messages.Code.ABORT)
        self.assertEqual(message.reason, 'tornwamp.error.unauthorized')
        self.assertEqual(message.details['message'], "Denied")

        msg = yield ws.read_message()
        self.assertIs(msg, None)
        self.assertEqual(ws.close_code, 1)
        self.assertEqual(ws.close_reason, "Denied")

    @gen_test
    def test_goodbye_message_closes_connection(self):
        request = self.build_request()
        ws = yield websocket_connect(request)

        msg = messages.GoodbyeMessage(details={"message": "Closing for test purposes"}, reason="close.up")
        ws.write_message(msg.json)

        text = yield ws.read_message()
        message = messages.GoodbyeMessage.from_text(text)
        self.assertIs(message.code, messages.Code.GOODBYE)
        self.assertEqual(message.reason, 'close.up')
        self.assertEqual(message.details['message'], "Closing for test purposes")

        msg = yield ws.read_message()
        self.assertIs(msg, None)
        self.assertEqual(ws.close_code, 1000)
        self.assertEqual(ws.close_reason, "Closing for test purposes")

    @gen_test
    def test_goodbye_unsubscribes_connection(self):
        request = self.build_request()
        ws = yield websocket_connect(request)

        msg = messages.SubscribeMessage(request_id=5, topic="announcements")
        ws.write_message(msg.json)
        text = yield ws.read_message()
        message = messages.SubscribedMessage.from_text(text)
        self.assertEqual(message.request_id, 5)
        self.assertEqual(len(tornwamp_topic.topics["announcements"].subscribers), 1)

        msg = messages.GoodbyeMessage(details={"message": "Closing for test purposes"}, reason="close.up")
        ws.write_message(msg.json)
        yield ws.read_message()
        self.assertEqual(len(tornwamp_topic.topics["announcements"].subscribers), 0)

    @gen_test
    @patch("tornwamp.processors.pubsub.customize.authorize_subscription", return_value=(True, ""))
    def test_publish_event(self, mock_authorize):
        connection_subscriber = MockConnection()
        tornwamp_topic.topics.add_subscriber(
            "interstellar",
            connection_subscriber
        )

        request = self.build_request()
        ws = yield websocket_connect(request)

        options = {"acknowledge": True}
        msg = messages.PublishMessage(request_id=1, topic="interstellar", kwargs={"review": "Mind blowing"}, options=options)
        ws.write_message(msg.json)

        text = yield ws.read_message()
        published_msg = messages.PublishedMessage.from_text(text)
        self.assertEqual(published_msg.request_id, 1)

        text = connection_subscriber._websocket.message
        event_msg = messages.EventMessage.from_text(text)
        self.assertEqual(event_msg.kwargs, {u'review': u'Mind blowing'})

    @gen_test
    def test_ping_rpc(self):
        request = self.build_request()
        ws = yield websocket_connect(request)

        msg = messages.CallMessage(request_id=1, procedure="ping")
        ws.write_message(msg.json)

        text = yield ws.read_message()
        message = messages.ResultMessage.from_text(text)
        self.assertIs(message.code, messages.Code.RESULT)
        self.assertEqual(message.args, ['Ping response'])

    @gen_test
    @patch("tornwamp.processors.pubsub.customize.authorize_subscription", return_value=(True, ""))
    def test_broadcasting_rpc(self, mock_authorization):
        connection_subscriber = MockConnection()
        tornwamp_topic.topics.add_subscriber(
            "interstellar",
            connection_subscriber
        )

        request = self.build_request()
        ws = yield websocket_connect(request)

        def test(call_message, connection):
            assert connection
            answer = messages.ResultMessage(
                request_id=call_message.request_id,
                details=call_message.details,
                args=["It works"]
            )
            event_msg = messages.EventMessage(publication_id=1, kwargs={u'review': u'Mind blowing'})
            return answer, [messages.BroadcastMessage("interstellar", event_msg, connection.id)]

        rpc.customize.procedures["test"] = test

        msg = messages.CallMessage(request_id=1, procedure="test")
        ws.write_message(msg.json)

        text = yield ws.read_message()
        message = messages.ResultMessage.from_text(text)
        self.assertIs(message.code, messages.Code.RESULT)
        self.assertEqual(message.args, ['It works'])

        text = connection_subscriber._websocket.message
        event_msg = messages.EventMessage.from_text(text)
        self.assertEqual(event_msg.kwargs, {u'review': u'Mind blowing'})
