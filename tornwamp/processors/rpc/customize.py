"""
This module allows customization of which methos are supported when using
RPC.
"""

from tornwamp.messages import ResultMessage

ping = lambda call_message, connection: ResultMessage(
    request_id=call_message.request_id,
    details=call_message.details,
    args=["Ping response"]
)

procedures = {
    "ping": ping
}
