Python Hottop Client
====================
.. image:: https://readthedocs.org/projects/pyhottop/badge/?version=latest
    :target: http://pyhottop.readthedocs.io/en/latest/?badge=latest

.. image:: https://badge.fury.io/py/pyhottop.svg
    :target: https://badge.fury.io/py/pyhottop


pyHottop gives you the power to control your Hottop KN-8828b-2k+ roaster directly through python code. **This library is meant to be used within applications and should not be used by itself to conduct a roast**. Questions, comments or for support needs, please use the issues_ page on Github.

.. _issues: https://github.com/splitkeycoffee/pyhottop/issues


Getting Started
---------------

In order to interact with your Hottop roaster, you need to ensure your model has a USB-serial port which comes standard with the KN-8828b-2k+.

1. Install the CP210x USB driver to read from the serial port:

https://www.silabs.com/products/development-tools/software/usb-to-uart-bridge-vcp-drivers

2. Install the pyHotop module:

``pip install pyhottop`` or ``python setup.py install``

3. Plug your Hottop roaster into your laptop.
4. Test connectivity to the roaster by running the diagnostic utility:

``pyhottop-test test``


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

Changelog
---------

2017-12-02
~~~~~~~~~~
* Bugfix: Called the proper logging object on buffer measurement
* Change: Added raw buffer responses to the event log
* Feature: Added a validate routine to the buffer read to account for inaccurate responses from the roaster
* Feature: Automatically derive charge and turning point events based on temperature data

2017-12-01
~~~~~~~~~~
* Bugfix: Turned drum motor on when doing a cool-down to push beans out

2017-11-29
~~~~~~~~~~
* Bugfix: Replaced existing extenal_temp with environment_temp
* Bugfix: Fixed issue with buffer retry loop where it was not being called
* Change: Adjusted default interval to 1 second to avoid buffer issues
* Change: Toggle serial connection if having trouble reading buffer

2017-11-28
~~~~~~~~~~
* Change: Adjusted duration to be of format MM:SS instead of total seconds
* Change: Return roast state when toggling monitoring

2017-11-24
~~~~~~~~~~
* Feature: several new methods for getting additional roast details
* Change: Refactored code related to tracking roast properties and timing
* Change: Updated documentation within the code
* Bugfix: when running with python3 due to queue library

