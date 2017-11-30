Changelog
=========
Running list of changes to the library.

2017-11-29
~~~~~~~~~~
* Bugfix: Replaced existing extenal_temp with environment_temp
* Bugfix: Fixed issue with buffer retry loop where it was not being called
* Change: Adjusted default interval to 1 second to avoid buffer issues
* Change: Toggle serial connection if having trouble reading buffer

2017-11-28
----------
* Change: Adjusted duration to be of format MM:SS instead of total seconds
* Change: Return roast state when toggling monitoring

2017-11-24
----------
* Feature: several new methods for getting additional roast details
* Change: Refactored code related to tracking roast properties and timing
* Change: Updated documentation within the code
* Bugfix: when running with python3 due to queue library

