Code Documentation
===================

Hottop Interface
----------------

This is the primary class that you will interact with when building applications for the Hottop roaster. This class will automatically spawn a threaded instance of the control process which will handle the core of the operations against the roaster.

.. autoclass:: pyhottop.pyhottop.Hottop
    :members:
    :private-members:

Control Process
---------------

Due to the nature of continuously needing to poll the serial interface, a thread was required to handle interactions with the serial interface. It's possible to use the multiprocessing module to handle this work, but when using this library inside of web server technology, multiprocessing often causes issues. Vanilla threads were used here to avoid interaction problems with co-routine or eventlet-based libraries.

.. autoclass:: pyhottop.pyhottop.ControlProcess
    :members:
    :private-members: