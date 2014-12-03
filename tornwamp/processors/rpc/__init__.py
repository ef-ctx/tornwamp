"""
RPC processors.

Compatible with WAMP Document Revision: RC3, 2014/08/25, available at:
https://github.com/tavendo/WAMP/blob/master/spec/basic.md
"""

from tornwamp.messages import CallMessage, ResultMessage, ErrorMessage
from tornwamp.processors import Processor
from tornwamp.processors.rpc import customize


class CallProcessor(Processor):
    """
    Responsible for dealing with CALL messages.
    """

    def process(self):
        """
        Call method defined in tornwamp.customize.procedures (dict).

        Each method should return:
        - RESPONSE
        - ERROR

        Which will be the processor's answer message.'
        """
        msg = CallMessage(*self.message.value)
        direct_messages = []
        method_name = msg.procedure
        if (method_name in customize.procedures):
            method = customize.procedures[method_name]
            answer, direct_messages = method(*msg.args, call_message=msg, connection=self.connection, **msg.kwargs)
        else:
            error_uri = "wamp.rpc.unsupported.procedure"
            error_msg = "The procedure {} doesn't exist".format(method_name)
            response_msg = ErrorMessage(
                request_code=msg.code,
                request_id=msg.request_id,
                details={"call": msg.json},
                uri=error_uri
            )
            response_msg.error(error_msg)
            answer = response_msg
        self.answer_message = answer
        self.direct_messages = direct_messages
