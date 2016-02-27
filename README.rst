.. image:: https://travis-ci.org/ef-ctx/tornwamp.svg?branch=master
    :target: https://travis-ci.org/ef-ctx/tornwamp

.. image:: https://coveralls.io/repos/github/ef-ctx/tornwamp/badge.svg?branch=master
    :target: https://coveralls.io/github/ef-ctx/tornwamp?branch=master 

.. image:: https://img.shields.io/pypi/v/tornwamp.svg
    :target: https://pypi.python.org/pypi/tornwamp/

.. image:: https://img.shields.io/pypi/pyversions/tornwamp.svg
    :target: https://pypi.python.org/pypi/tornwamp/

.. image:: https://img.shields.io/pypi/dm/tornwamp.svg
    :target: https://pypi.python.org/pypi/tornwamp/

TornWAMP
========

This Python module implements parts of `WAMP <http:/git/wamp.ws/>`_
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

   Copyright 2015, Education First

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
