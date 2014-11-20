"""
TornWAMP user-configurable structures.
"""
from tornwamp.processors import GoodbyeProcessor, HelloProcessor

processors = {
    1: HelloProcessor,
    6: GoodbyeProcessor
}
#    2: 'welcome',
#    3: 'abort',
#    4: 'challenge',
#    5: 'authenticate',
#    7: 'heartbeat',
#    8: 'error',
#    16: 'publish',
#    17: 'published',
#    32: 'subscribe',
#    33: 'subscribed',
#    34: 'unsubscribe',
#    35: 'unsubscribed',
#    36: 'event',
#    48: 'call',
#    49: 'cancel',
#    50: 'result',
#    64: 'register',
#    65: 'registered',
#    66: 'unregister',
#    67: 'unregistered',
#    68: 'invocation',
#    69: 'interrupt',
#    70: 'yield'
