Getting Started
===============

In order to interact with your Hottop roaster, you need to ensure your model has a USB-serial port which comes standard with the KN-8828b-2k+.

1. Install the CP210x USB driver to read from the serial port:

https://www.silabs.com/products/development-tools/software/usb-to-uart-bridge-vcp-drivers

2. Install the pyHotop module:

``pip install pyhottop`` or ``python setup.py install``

3. Plug your Hottop roaster into your laptop.
4. Test connectivity to the roaster by running the diagnostic utility:

``pyhottop-test test``