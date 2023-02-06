#
# Copyright (C) 2023 Scott Dixon
# This software is distributed under the terms of the MIT License.
#
"""
    Command Line Interface
"""
import abc
import argparse
import asyncio
import typing
import logging

from .. import Servo


class AsyncRunner(abc.ABC):
    def __init__(self, args: argparse.Namespace):
        self._args = args
        self._logger = logging.getLogger(self.__class__.__name__)
    
    @abc.abstractmethod
    async def run(self) -> int:
        pass


class AsyncServoRunner(AsyncRunner):

    @classmethod
    def visit_add_parser(self, sub_parsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
        return sub_parsers.add_parser("servo", help="Commands to work with the pan/tilt servos.")

    @classmethod
    def visit_setargs(self, parser: argparse.ArgumentParser) -> typing.List[argparse.ArgumentParser]:
        sub_parsers: argparse._SubParsersAction = parser.add_subparsers(title="servo commands", dest="_sub_command")
        ping = sub_parsers.add_parser("ping")
        home = sub_parsers.add_parser("home")
        
        return [ping, home]

    async def run(self) -> int:
        
        if not hasattr(self._args, "_sub_command"):
            setattr(self._args, "_sub_command", "<unknown>")
        sub_command: str = self._args._sub_command
        if sub_command == "ping":
            servo_1 = Servo("/dev/ttyUSB0", 1)
            servo_2 = Servo("/dev/ttyUSB0", 2)
            async with servo_1 as pan_servo:
                async with servo_2 as tilt_servo:
                    await asyncio.gather(pan_servo.ping(), tilt_servo.ping())
        elif sub_command == "home":
            async with Servo("/dev/ttyUSB0", 1) as pan_servo:
                async with Servo("/dev/ttyUSB0", 2) as tilt_servo:
                    await asyncio.gather(pan_servo.home(), tilt_servo.home())
        else:
            self._logger.debug("Unknown sub command {}".format(sub_command))
            return -2
            
        return 0
