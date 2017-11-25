.. pyHottop documentation master file, created by
   sphinx-quickstart on Thu Nov  9 10:39:13 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Python Hottop Client
====================
pyHottop gives you the power to control your Hottop KN-8828b-2k+ roaster directly through python code. **This library is meant to be used within applications and should not be used by itself to conduct a roast**. Questions, comments or for support needs, please use the issues_ page on Github.

.. _issues: https://github.com/9b/pyhottop/issues


Features
--------

This library provides full control of the Hottop roaster. Built-in callback functionality allows you to build applications that decouple the processing logic from the library from the core of your application.

* Stream Hottop readings
    * Easy-to-use callbacks that return readings
    * Adjustable polling interval
    * Human-readable settings
    * Flexible collection of data
    * Debugging interface
* Control the Hottop directly
    * Heater settings
    * Fan speeds
    * Drum motor toggle
    * Cooling motor toggle
    * Solenoid (drum door) toggle
    * Chaff tray (detection) reader
* Auto-discover roaster connection
    * Loops over USB connections to find the proper serial


Code Documentation
------------------

.. toctree::
   :maxdepth: 2

   introduction
   code
   exceptions
   changelog

License
-------
Copyright 2017 Split Key Coffee

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

