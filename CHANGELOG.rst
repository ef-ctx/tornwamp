Version 2.0.0 (2017-01-06)
--------------------------

This new version has a few breaking changes needed when adding support for
redis pub/sub.

* Processors do not have direct_messages attribute anymore. Instead,
  broadcast_message attribute should be used.
* pubsub.customize has the following changes

    - add_subscriber
    - get_subscribe_direct_messages
    - get_publish_direct_messages
    + get_subscribe_broadcast_message

  In order to generate a message from SubscriberProcessor
  get_subscribe_broadcast_message should be overridden. The default behavior is
  not to generate any messages.
* topic.customize has deliver_event_messages method which should be used to
  cutomize which websocket connections should receive the message (this takes
  the role which was performed by direct_messages attribute and the second
  element of the tuple returned by rpc calls)
* The second element on the tuple returned by rpc calls need to be either None
  or a BroadcastMessage
* Added support for redis pubsub, allowing multiple tornwamp instances to
  communicate.
  
