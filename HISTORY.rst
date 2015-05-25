.. :changelog:

History
-------

0.3.0 (2015-05-25)
^^^^^^^^^^^^^^^^^^

* Added update_buffer option (enabled by default) to RTMP.create_stream,
  which enables a hack to increase throughput.
* Added a update_buffer method to RTMPStream.
* We now require at least version 1.0.1 of cffi.


0.2.2 (2015-04-15)
^^^^^^^^^^^^^^^^^^

* Fixed proxy not being used by librtmp.
* Added support for Cygwin, patch by @schrobby. (#17)


0.2.1 (2014-09-01)
^^^^^^^^^^^^^^^^^^

* Fixed expected bytes type on Python 2.
* Fixed singledispatch dependency condition.


0.2.0 (2014-04-07)
^^^^^^^^^^^^^^^^^^

* RTMPError now inherits from IOError.
* Fixed MSVC build.
* Added librtmp.so.1 to library paths, patch by Athanasios Oikonomou. (#4)
* Added librtmp.dylib to library paths, patch by Will Donohoe. (#6)


0.1.2 (2013-10-08)
^^^^^^^^^^^^^^^^^^

* Fixed compilation issue on some platforms.
* Fixed AMF issue on older librtmp versions. (#1)


0.1.1 (2013-09-25)
^^^^^^^^^^^^^^^^^^

* Fixed packaging issues.


0.1.0 (2013-09-23)
^^^^^^^^^^^^^^^^^^

* First release on PyPI.
