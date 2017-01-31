import greenlet
from tornado.concurrent import Future
from tornado.testing import AsyncTestCase

from tornwamp import utils


class UtilsTestCase(AsyncTestCase):

    def test_successful_future(self):
        future = Future()

        def run():
            ret = utils.run_async(future)
            self.stop()
            self.assertEqual(ret, "banana")

        gr = greenlet.greenlet(run)
        gr.switch()

        future.set_result("banana")
        self.wait()

    def test_unsuccessful_future(self):
        class BadFuture(Exception):
            pass

        future = Future()

        def run():
            with self.assertRaises(BadFuture):
                utils.run_async(future)
            self.stop()

        gr = greenlet.greenlet(run)
        gr.switch()

        future.set_exception(BadFuture("you have been exterminated"))
        self.wait()
