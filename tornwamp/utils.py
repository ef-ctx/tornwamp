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

    if future.exception():
        raise future.exception()
    else:
        return future.result()
