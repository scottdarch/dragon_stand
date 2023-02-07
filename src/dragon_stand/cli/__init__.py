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
import typing
from .runners import AsyncRunner, AsyncServoRunner

    
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
    
    sub_parsers: argparse._SubParsersAction = parser.add_subparsers(title="Commands", dest="command")
    servo_parser = AsyncServoRunner.visit_add_parser(sub_parsers)
    subcommands = AsyncServoRunner.visit_setargs(servo_parser)
    servo_parser.set_defaults(_runner=AsyncServoRunner, _sub_command_parsers=subcommands)

    return parser

async def main() -> int:
    """
    Main entry point for running this library as a CLI.
    """

    #
    # Parse the command-line arguments.
    #
    parser = _make_parser()
    args = parser.parse_args()

    #
    # Setup Python logging.
    #
    fmt = "%(message)s"
    level = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}.get(args.verbose or 0, logging.DEBUG)
    logging.basicConfig(stream=sys.stderr, level=level, format=fmt)

    logging.debug("Running %s using sys.prefix: %s", pathlib.Path(__file__).name, sys.prefix)

    runner_type: typing.Optional[typing.Type[AsyncRunner]] = getattr(args, "_runner", None)
    
    if runner_type is not None:
        runner = runner_type(args)

        run_result = await runner.run()
    else:
        run_result = -2
    
    if run_result == -2:
        parser.print_help()
        sub_command_parsers: typing.Optional[typing.List[argparse.ArgumentParser]] = getattr(args, "_sub_command_parsers", None)
        if sub_command_parsers is not None and len(sub_command_parsers) > 0:
            print("+---[command help: {}]------+".format(args.command))
            for sub_command_parser in sub_command_parsers:
                sub_command_parser.print_help()
        return 0
    else:
        return run_result
