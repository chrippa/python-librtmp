python-librtmp
==============

.. image:: http://img.shields.io/pypi/v/python-librtmp.svg?style=flat-square
    :target: https://pypi.python.org/pypi/python-librtmp

.. image:: http://img.shields.io/pypi/dm/python-librtmp.svg?style=flat-square
    :target: https://pypi.python.org/pypi/python-librtmp

.. image:: http://img.shields.io/travis/chrippa/python-librtmp.svg?style=flat-square
    :target: http://travis-ci.org/chrippa/python-librtmp


python-librtmp is a `RTMP`_ client library. It uses the implementation
provided by `librtmp`_ via `cffi`_.

* Free software: `BSD license`_
* Documentation: http://pythonhosted.org/python-librtmp


.. _RTMP: http://en.wikipedia.org/wiki/Real_Time_Messaging_Protocol
.. _cffi: http://cffi.readthedocs.org/
.. _librtmp: http://rtmpdump.mplayerhq.hu/librtmp.3.html
.. _BSD license: http://opensource.org/licenses/BSD-2-Clause


Installation
============

The latest stable version is available to install using `pip`_

.. code-block:: console

    sudo pip install python-librtmp

But you can also get the development version using `Git <http://git-scm.com/>`_:

.. code-block:: console

    git clone git://github.com/chrippa/python-librtmp.git
    cd python-librtmp
    sudo python setup.py install


.. _pip: http://pip-installer.org/
.. _git: http://git-scm.com/

.. note::

    `cffi`_ 1.0 was released recently which contains significant changes. If you have
    an old version already installed you will have to manually upgrade it or
    you will get an error when attempting to install python-librtmp.


Dependencies
------------

- `Python`_, at least version 2.6 or 3.3.
- a C compiler capapable of building `Python`_ extensions, e.g. `gcc`_
- `librtmp`_: The library including its headers (`librtmp-dev` or equivalent)
- `cffi`_: cffi depends on libffi and its headers (`libffi-dev` or equivalent)
- On Python <3.4 the backport of `singledispatch`_ is also required.

.. _gcc: https://gcc.gnu.org/
.. _python: http://python.org/
.. _singledispatch: https://pypi.python.org/pypi/singledispatch


Windows
-------

python-librtmp (and `cffi`_) has wheel packages (binaries) available on PyPi and can
therefore be easily installed with `pip 1.4+ <http://www.pip-installer.org/>`_
without the need to compile anything:

.. code-block:: console

    > pip install python-librtmp

    (on older pip versions you need to use --use-wheel)
    > pip install --use-wheel python-librtmp


Features
========

Streaming
---------

The most common use case of RTMP is to read a video stream from
a server.

.. code-block:: python

    import librtmp

    # Create a connection
    conn = librtmp.RTMP("rtmp://your.server.net/app/playpath", live=True)
    # Attempt to connect
    conn.connect()
    # Get a file-like object to access to the stream
    stream = conn.create_stream()
    # Read 1024 bytes of data
    data = stream.read(1024)


Remote function calls
---------------------

Here is a example of creating a Python function that can be used to call
remote functions:

.. code-block:: python

    my_remote_method = conn.remote_method("MyRemoteMethod", block=True)
    result = my_remote_method("some argument")

Waiting for the server to call our function:

.. code-block:: python

    # This will automatically name the function after it's Python name
    @conn.invoke_handler
    def my_add(a, b):
        return a + b

    # Start waiting for calls
    conn.process_packets()

You can also use custom function name instead:

.. code-block:: python

    @conn.invoke_handler("MyMath.MyAdd")

Instead of blocking forever when waiting for a call you can specify to wait
only for a specific invoke and then stop blocking:

.. code-block:: python

    conn.process_packets(invoked_method="MyMath.MyAdd", timeout=30)


