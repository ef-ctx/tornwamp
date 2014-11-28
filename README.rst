TornWAMP
========

This Python module implements parts of `WAMP <http://wamp.ws/>`_
(Web Application Messaging Protocol).

TornWAMP provides means of having an API which interacts with WAMP-clients
(e.g. `Autobahn <http://autobahn.ws/>`_).

TornWAMP is not a WAMP Client nor a WAMP Router. 

Although this code was implemented to be used with Websockets and
`Tornado <http://www.tornadoweb.org/>`_ (Web framework),
it can also be used in other ways.


How to install
==============

Using `pip <https://pip.pypa.io/>`_ (to be available soon):

::

    pip install tornwamp

Or from the source-code:

::

    git clone https://github.com/ef-ctx/tornwamp.git
    cd tornwamp
    python setup.py install


Example of usage
================

An example of how to build a server using TornWAMP (`wamp.py`):

::

    import tornado
    import tornwamp

    class SampleHandler(tornwamp.WAMPHandler):
        pass

    application = tornado.web.Application([
        (r"/ws", SampleHandler),
    ])

    if __name__ == "__main__":
        application.listen(8888)
        tornado.ioloop.IOLoop.instance().start()

Which can be run:

::

    python wamp.py


From the client perspective, you'd be able to use Autobahn JavaScript library
to connect to the server using:

::

  var connection = new autobahn.Connection({
    url: "ws://0.0.0.0:8888/ws",
    realm: "sample"
  });


License
=======

TornWAMP is GNU GPL 2:

< TornWAMP >
Copyright (C) 2014 - Education First (CTX Team)

Tornado WAMP is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 2 of the License.

Tornado WAMP is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Tornado WAMP. If not, see <http://www.gnu.org/licenses/>.
