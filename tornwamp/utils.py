from functools import partial

import greenlet
from tornado import ioloop


def run_async(future):
    """
    Uses greenlet to return to this point after future is finished executing.
    """
    gr = greenlet.getcurrent()
    ioloop.IOLoop.current().add_future(future, gr.switch)

    future = gr.parent.switch()

    # The following lines are actually covered in tests/unit/test_utils.py,
    # however, coverage is not able to report it (even with concurrency =
    # greenlet!). Maybe it is due to the intarction with both greenlet and
    # tornado.
    if future.exception():  # pragma: no cover
        raise future.exception()
    else:  # pragma: no cover
        return future.result()
