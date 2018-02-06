"""
This module allows customization of which methos are supported when using
RPC.

The key of the procedures dict is the name of the procedure as received
when CALL is invoked. Each procedure should return a ResultMessage and a
list of BroadcastMessages. The former is returned to the caller of the
procedure, the later describes the notification message to be
broadcasted to the other active connections (further restrictions to the
broadcasted message can be added in the delivery methods).
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
