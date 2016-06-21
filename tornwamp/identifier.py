"""
Compatible with WAMP Document Revision: RC3, 2014/08/25.

WAMP Identifiers definition is available at:
https://github.com/tavendo/WAMP/blob/master/spec/basic.md#ids


{citation}

WAMP needs to identify the following ephemeral entities each in the scope noted

- Sessions (global scope)
- Publications (global scope)
- Subscriptions (router scope)
- Registrations (router scope)
- Requests (session scope)

These are identified in WAMP using IDs that are integers between (inclusive) 0
and 2^53 (9007199254740992):

IDs in the global scope MUST be drawn randomly from a uniform distribution over
the complete range [0, 2^53]

IDs in the router scope can be chosen freely by the specific router
implementation

IDs in the session scope SHOULD be incremented by 1 beginning with 1 (for each
direction - Client-to-Router and Router-to-Client)

{citation}
"""
import random

MIN_ID = 0
MAX_ID = 2 ** 53

existing_ids = []


def create_global_id():
    """
    Return a global scope ID, which is not in existing_ids list provided.
    This function also appends new ID to original existing_ids list.

    According to WAMP specification:
    "IDs in the global scope MUST be drawn randomly from a uniform distribution
    over the complete range [0, 2^53]"
    """
    new_id = None
    while new_id not in existing_ids:
        candidate_id = random.randint(MIN_ID, MAX_ID)
        if candidate_id not in existing_ids:
            new_id = candidate_id
            existing_ids.append(new_id)
    return new_id
