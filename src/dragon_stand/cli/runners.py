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
        subparser: argparse.ArgumentParser = sub_parsers.add_parser("servo", help="Commands to work with the pan/tilt servos.")
        subparser.add_argument("--port", default="/dev/ttyUSB0")
        return subparser

    @classmethod
    def visit_setargs(self, parser: argparse.ArgumentParser) -> typing.List[argparse.ArgumentParser]:
        sub_parsers: argparse._SubParsersAction = parser.add_subparsers(title="servo commands", dest="_sub_command")
        ping = sub_parsers.add_parser("ping")
        home = sub_parsers.add_parser("home")
        query = sub_parsers.add_parser("query")
        query.add_argument("-id", help="The servo to query.", type=int)
        
        return [ping, home, query]

    async def run(self) -> int:
        
        port: str = self._args.port
        if not hasattr(self._args, "_sub_command"):
            setattr(self._args, "_sub_command", "<unknown>")
        sub_command: str = self._args._sub_command
        if sub_command == "ping":
            servo_1 = Servo(port, 1)
            servo_2 = Servo(port, 2)
            async with servo_1 as pan_servo:
                async with servo_2 as tilt_servo:
                    await asyncio.gather(pan_servo.ping(), tilt_servo.ping())
        elif sub_command == "home":
            async with Servo(port, 1) as pan_servo:
                async with Servo(port, 2) as tilt_servo:
                    await asyncio.gather(pan_servo.home(4082), tilt_servo.home(4082))
        elif sub_command == "query":
            try:
                async with Servo(port, self._args.id, enable_torque_on_connect=False) as servo:
                    while True:
                        pos = await servo.current_position()
                        print("{}: Servo {} -> {}".format(port, self._args.id, pos))
                        await asyncio.sleep(1)
            except KeyboardInterrupt as _:
                print("done")
        else:
            self._logger.debug("Unknown sub command {}".format(sub_command))
            return -2
            
        return 0
