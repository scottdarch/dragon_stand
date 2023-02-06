#
# Copyright (C) 2023 Scott Dixon
# This software is distributed under the terms of the MIT License.
#
"""
Utilities for working with the Dynamixel servos on the test stand.
"""
import abc
import asyncio
import contextlib
import logging
import typing
import types
from contextlib import asynccontextmanager

from . import dynamixel_sdk

class _ServoCommunicationError(RuntimeError):
    pass

class _Servo(contextlib.AbstractAsyncContextManager):

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

    async def __aenter__(self):
        if await self.connect():
            return self
        else:
            return None

    async def __aexit__(self,
                        exc_type: typing.Optional[typing.Type[BaseException]],
                        exc: typing.Optional[BaseException], 
                        exc_trace: typing.Optional[types.TracebackType]):
        if self.is_connected:
            await self.disconnect()

    @abc.abstractmethod
    async def connect(self) -> bool:
        pass

    @abc.abstractmethod
    async def disconnect(self) -> None:
        pass

    @abc.abstractproperty
    def is_connected(self) -> bool:
        pass


class _Dynamixel(_Servo):
    DEFAULT_BAUDRATE = 57600
    # Control table address
    ADDR_MX_TORQUE_ENABLE       = 24
    ADDR_MX_GOAL_POSITION       = 30
    ADDR_MX_PRESENT_POSITION    = 36
    
    def __init__(self, device_name: str, device_id: int, protocol_version: float = 1.0):
        super().__init__()
        self._port_handler = dynamixel_sdk.PortHandler(device_name)
        self._device_id = device_id
        self._packet_handler = dynamixel_sdk.Protocol1PacketHandler()
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    async def connect(self) -> bool:
        if not self._port_handler.openPort():
            return False
        try:
            self._connected = self._port_handler.setBaudRate(self.DEFAULT_BAUDRATE)
            result, error = self._write1ByteTxRx(self.ADDR_MX_TORQUE_ENABLE, 1)
            if result != dynamixel_sdk.COMM_SUCCESS:
               raise _ServoCommunicationError("Failed to enable torque")
            else:
                self._logger.debug("Dynamixel has been successfully connected")
            return self._connected
        except:
            await self.disconnect()
            raise

    async def disconnect(self) -> None:
        if self._connected:
            result, error = self._write1ByteTxRx(self.ADDR_MX_TORQUE_ENABLE, 0)
            if result != dynamixel_sdk.COMM_SUCCESS:
               self._logger.warning("Failed to disable torque")
            else:
                self._logger.debug("Dynamixel has been successfully connected")
        self._port_handler.closePort()
        self._connected = False

    async def ping(self) -> bool:
        dxl_model_number, dxl_comm_result, dxl_error = self._packet_handler.ping(self._port_handler, self._device_id)
        if dxl_comm_result != dynamixel_sdk.COMM_SUCCESS:
            print("%s" % self._packet_handler.getTxRxResult(dxl_comm_result))
            return False
        elif dxl_error != 0:
            print("%s" % self._packet_handler.getRxPacketError(dxl_error))
            return False
        else:
            print("[ID:%03d] ping Succeeded. Dynamixel model number : %d" % (self._device_id, dxl_model_number))
            return True

    async def home(self) -> bool:
        goal_pos = 0x800
        result, error = self._write2ByteTxRx(self.ADDR_MX_GOAL_POSITION, goal_pos)
        if result != dynamixel_sdk.COMM_SUCCESS:
            return False
        
        data = 0xFFFFFF
        while data != goal_pos:
            await asyncio.sleep(.1)
            data, result, error = self._read2ByteTxRx(self.ADDR_MX_PRESENT_POSITION)
            if result != dynamixel_sdk.COMM_SUCCESS or error != 0:
                return False
            else:
                self._logger.debug("Current position ({}): {}".format(self._device_id, data))
        
        return True
    
    def _read2ByteTxRx(self, addr: int) -> typing.Tuple[int, int, int]:
        return self._packet_handler.read2ByteTxRx(self._port_handler,
                                     self._device_id, 
                                     addr)

    def _write2ByteTxRx(self, addr: int, value: int) -> typing.Tuple[int, int]:
        return self._packet_handler.write2ByteTxRx(self._port_handler,
                                     self._device_id, 
                                     addr,
                                     value)

    def _write1ByteTxRx(self, addr: int, value: int) -> typing.Tuple[int, int]:
        return self._packet_handler.write1ByteTxRx(self._port_handler,
                                     self._device_id, 
                                     addr,
                                     value)
    
    