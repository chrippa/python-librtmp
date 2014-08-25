===============================
python-librtmp
===============================

.. image:: http://img.shields.io/pypi/v/python-librtmp.svg?style=flat-square
    :target: https://pypi.python.org/pypi/python-librtmp

.. image:: http://img.shields.io/pypi/dm/python-librtmp.svg?style=flat-square
    :target: https://pypi.python.org/pypi/python-librtmp

.. image:: http://img.shields.io/travis/chrippa/python-librtmp.svg?style=flat-square
    :target: http://travis-ci.org/chrippa/python-librtmp



python-librtmp is a Python interface to librtmp.
It uses `cffi <http://cffi.readthedocs.org/>`_ to interface with
the C library `librtmp <http://rtmpdump.mplayerhq.hu/librtmp.3.html>`_.

* Free software: BSD license
* Documentation: http://pythonhosted.org/python-librtmp


Installation
------------

The latest stable version is available to install using `pip <http://www.pip-installer.org/>`_:

.. code-block:: console

    # pip install cffi
    # pip install python-librtmp

But you can also get the development version using `Git <http://git-scm.com/>`_:

.. code-block:: console

    $ git clone git://github.com/chrippa/python-librtmp.git
    $ cd python-librtmp
    # pip install cffi
    # python setup.py install


Dependencies
^^^^^^^^^^^^

- a compiler, e.g `gcc`
- librtmp: The library including it's headers (`librtmp-dev`). Only the official librtmp is supported, patched versions such as librtmp-ksv may not work.
- cffi: The setup.py script currently depends on cffi being installed.
  Therefore you need to install it before installing this library.
  cffi also depends on libffi and it's headers (`libffi-dev`)


Windows
^^^^^^^

python-librtmp (and cffi) has wheel packages (binaries) available on PyPi and can
therefore be easily installed with `pip 1.4+ <http://www.pip-installer.org/>`_
without the need to compile anything:

.. code-block:: console

    > pip install --use-wheel python-librtmp


Features
--------

Streaming
^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^^^^

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


