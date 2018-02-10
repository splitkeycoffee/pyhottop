#!/usr/bin/env python
"""Test the USB serial interface to see if it can connect to a roaster.

This command lone tool simply makes it easy to understand if the roaster can
be accessed via a USB interface. Default settings will attempt to discover the
port used by the roaster. The port can be specified via the `--interface`
command.
"""
__author__ = "Brandon Dixon"
__copyright__ = "Copyright, Split Key Coffee"
__credits__ = ["Brandon Dixon"]
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Brandon Dixon (brandon@splitkeycoffee.com)"
__email__ = "info@splitkeycoffee.com"
__status__ = "BETA"

import sys
from pyhottop.pyhottop import Hottop, SerialConnectionError
from argparse import ArgumentParser


def main():
    """Run the core."""
    parser = ArgumentParser()
    subs = parser.add_subparsers(dest='cmd')

    setup_parser = subs.add_parser('test')
    setup_parser.add_argument('--interface', default=None,
                              help='Manually pass in the USB connection.')
    args = parser.parse_args()

    if args.cmd == 'test':
        ht = Hottop()
        try:
            if args.interface:
                ht.connect(interface=args.interface)
            ht.connect()
        except SerialConnectionError as e:
            print("[!] Serial interface not accessible: %s" % str(e))
            sys.exit(1)
        print("[*] Successfully connected to the roaster!")


if __name__ == '__main__':
    main()
