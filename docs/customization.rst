Customization
=============

The WAMPHandler can be registered to a path in a tornado application
without changes. In order to add new RPC methods (by default only CALL
ping is implemented) or to add custom behavior whenever a client
subscribes or publishes to a topic, tornwamp defines a few hooks.

Customization can be done by changing variables inside cutomize modules.
These are the customizable modules:

- **tornwamp.processors.pubsub.customize:** the methods can be
  overwritten to define specific behaviors when subscribing to topics and
  publishing messages.
- **tornwamp.processors.rpc.customize:** procedure dictionary can be
  extended to include other RPC methods
- **tornwamp.topic.customize:** the method can be overwritten to
  redefine the behavior of delivering messages to clients
- **tornwamp.customize:** allows the extention of processors dict with
  new processors and the customization of broadcast_messages call

These customiztions will automatically affect the behavior of the
WAMPHandler. More information can be found in the pydocs.
