"""
This module allows customization of which methos are supported when using
RPC.
"""

from tornwamp.messages import ResultMessage


def ping(call_message, connection):
    """
    Return a answer (ResultMessage) and empty list direct_messages.
    """
    assert connection, "ping requires connection"

    answer = ResultMessage(
        request_id=call_message.request_id,
        details=call_message.details,
        args=["Ping response"]
    )
    return answer, []

procedures = {
    "ping": ping
}
