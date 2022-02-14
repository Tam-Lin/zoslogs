#!/usr/bin/env python3

"""Console script for zoslogs."""
import argparse
import sys

import logging

import gzip
import bz2

from src.zoslogs import zoslogs


def open_by_suffix(filename):
    if filename.endswith('.gz'):
        return gzip.open(filename, 'rt', encoding="ISO-8859-1",
                         errors="ignore")
    elif filename.endswith('.bz2'):
        return bz2.BZ2file(filename, 'rt', encoding="ISO-8859-1",
                           errors="ignore")
    else:
        return open(filename, 'r', encoding="ISO-8859-1",
                    errors="ignore")


def main():

    logger = logging.getLogger(__name__)

    """Console script for zoslogs."""
    parser = argparse.ArgumentParser(description="Parse one or more z/OS log "
                                                 "files")
    parser.add_argument('file', nargs='+', help="Files to parse")
    parser.add_argument('--message_id', dest="message_ids_to_include",
                        help="Only return certain messages ids",
                        action="append")
    parser.add_argument('--message_contains', help="Message text contains",
                        action="append")
    parser.add_argument('--print', help="Print matching messages",
                        action="store_true")
    parser.add_argument('--halt_on_error', help="Halt on any parsing error",
                        action="store_true")
    parser.add_argument("--debug", help="Print debug messages",
                        action="store_true")
    parser.add_argument("--verbosity", "-v", help="Verbosity level",
                        action="count")
    args = parser.parse_args()

    filters = dict()

    if args.debug is True:
        logging.basicConfig(level=logging.DEBUG)
    elif args.verbosity:
        if args.verbosity == 1:
            logging.basicConfig(level=logging.CRITICAL)
        elif args.verbosity == 2:
            logging.basicConfig(level=logging.ERROR)
        elif args.verbosity == 3:
            logging.basicConfig(level=logging.WARNING)
        elif args.verbosity == 4:
            logging.basicConfig(level=logging.INFO)
        else:
            logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.CRITICAL)

    if args.message_ids_to_include:
        filters["message_ids_to_include"] = args.message_ids_to_include
        logger.info("Looking for messages " +
                    str(filters["message_ids_to_include"]))

    if args.message_contains:
        filters["message_contains"] = args.message_contains
        logger.info("Looking for messages containing " +
                    str(filters["message_contains"]))

    for filename in args.file:

        if args.print:
            print(filename)

        logger.info("Processing " + filename)

        with open_by_suffix(filename) as file:
            logs = zoslogs.ZosLogs(file, filters,
                                   halt_on_errors=args.halt_on_error)

            if args.print:
                for message in logs:
                    print(message)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
