#
# Copyright (C) 2023 Scott Dixon
# This software is distributed under the terms of the MIT License.
#
"""
    Command Line Interface
"""

import argparse
import textwrap
import logging
import sys
import pathlib

def _make_parser() -> argparse.ArgumentParser:
    
    epilog = textwrap.dedent(
        """

        **Example Usage**::

            # TODO

    """
    )

    parser = argparse.ArgumentParser(
        description="Utilities for working with the l3xz dragon-head.",
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("--verbose", "-v", action="count", help="verbosity level (-v, -vv)")

    return parser

def main() -> int:
    """
    Main entry point for running this library as a CLI.
    """

    #
    # Parse the command-line arguments.
    #
    args = _make_parser().parse_args()

    #
    # Setup Python logging.
    #
    fmt = "%(message)s"
    level = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}.get(args.verbose or 0, logging.DEBUG)
    logging.basicConfig(stream=sys.stderr, level=level, format=fmt)

    logging.info("Running %s using sys.prefix: %s", pathlib.Path(__file__).name, sys.prefix)

    from .runners import ArgparseRunner

    runner = ArgparseRunner(args)
    runner.run()
    return 0
