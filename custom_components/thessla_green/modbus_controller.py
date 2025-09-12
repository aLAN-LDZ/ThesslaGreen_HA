import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Dict

from pymodbus.client import AsyncModbusTcpClient

_LOGGER = logging.getLogger(__name__)


@dataclass
class ControllerData:
    holding: Dict[int, int] = field(default_factory=dict)
    input: Dict[int, int] = field(default_factory=dict)
    coil: Dict[int, bool] = field(default_factory=dict)
    update_interval: float = 0.0


class ControllerException(Exception):
    def __init__(self, message):
        super().__init__(message)


class ThesslaGreenModbusController:

    def __init__(self, host: str, port: int, slave_id: int, update_interval: int = 30):
        self._host = host
        self._port = port
        self._slave = slave_id
        self._update_interval = update_interval

        self._client = AsyncModbusTcpClient(
            host=self._host,
            port=self._port,
            reconnect_delay=1,
            reconnect_delay_max=300,
            retries=10,
        )
        self._controller_lock = asyncio.Lock()

        self._last_update_timestamp: float = 0
        self._last_update_interval: float = 0

        self._holding_blocks = [
            (256, 2), (4192, 2), (4198, 1), (4208, 3), (4210, 1),
            (4224, 1), (4320, 1), (4387, 1),
            (8192, 2), (8208, 1), (8222, 2), (8330, 2), (8444, 1)
        ]
        self._input_blocks = [(16, 4), (22, 1)]
        self._coil_blocks = [(9, 3)]

    async def stop(self):
        async with self._controller_lock:
            _LOGGER.info("Stopping Modbus controller for %s:%d", self._host, self._port)
            self._client.close()

    async def fetch_data(self) -> ControllerData:
        async with self._controller_lock:
            await self._ensure_connected()

            data_holding: dict[int, int] = {}
            data_input: dict[int, int] = {}
            data_coil: dict[int, bool] = {}

            now = time.time()
            if self._last_update_timestamp:
                self._last_update_interval = now - self._last_update_timestamp
                _LOGGER.debug("Time since last update: %.2f seconds", self._last_update_interval)
            self._last_update_timestamp = now

            _LOGGER.debug("Reading all register blocks for slave %d", self._slave)

            # Read holding registers
            for start, count in self._holding_blocks:
                try:
                    result = await self._client.read_holding_registers(address=start, count=count,
                                                                       device_id=self._slave)
                    if result.isError():
                        raise ControllerException(f"Error reading holding registers {start}-{start + count - 1}")
                    for i, val in enumerate(result.registers):
                        data_holding[start + i] = val
                    _LOGGER.debug("Holding registers %d-%d read: %s", start, start + count - 1, result.registers)
                except Exception as e:
                    raise ControllerException(
                        f"Exception reading holding registers {start}-{start + count - 1}: {e}") from e

            # Read input registers
            for start, count in self._input_blocks:
                try:
                    result = await self._client.read_input_registers(address=start, count=count, device_id=self._slave)
                    if result.isError():
                        raise ControllerException(f"Error reading input registers {start}-{start + count - 1}")
                    for i, val in enumerate(result.registers):
                        data_input[start + i] = val
                    _LOGGER.debug("Input registers %d-%d read: %s", start, start + count - 1, result.registers)
                except Exception as e:
                    raise ControllerException(
                        f"Exception reading input registers {start}-{start + count - 1}: {e}") from e

            # Read coils
            for start, count in self._coil_blocks:
                try:
                    result = await self._client.read_coils(address=start, count=count, device_id=self._slave)
                    if result.isError():
                        raise ControllerException(f"Error reading coils {start}-{start + count - 1}")
                    for i, val in enumerate(result.bits):
                        data_coil[start + i] = bool(val)
                    _LOGGER.debug("Coils %d-%d read: %s", start, start + count - 1, result.bits)
                except Exception as e:
                    raise ControllerException(f"Exception reading coils {start}-{start + count - 1}: {e}") from e

            return ControllerData(
                holding=data_holding,
                input=data_input,
                coil=data_coil,
                update_interval=round(self._last_update_interval, 2)
            )

    async def write_register(self, address: int, value: int) -> bool:
        async with self._controller_lock:
            await self._ensure_connected()

            try:
                _LOGGER.debug("Writing register %d = %s (slave=%d)", address, value, self._slave)
                result = await self._client.write_register(address=address, value=value, device_id=self._slave)
                if result.isError():
                    raise ControllerException(f"Failed to write register {address} with value {value}")
                _LOGGER.info("Successfully wrote register %d = %s", address, value)
                return True
            except Exception as e:
                raise ControllerException(f"Exception writing register {address} = {value}: {e}") from e

    async def _ensure_connected(self):
        if self._client.connected:
            return

        _LOGGER.info("Attempting connection to Modbus server %s:%d", self._host, self._port)
        try:
            if await self._client.connect():
                _LOGGER.info("Successfully connected to Modbus server %s:%d", self._host, self._port)
                return
        except Exception as e:
            raise ControllerException(f"Exception during Modbus connection to {self._host}:{self._port}: {e}") from e

        raise ControllerException(f"Failed to connect to Modbus server {self._host}:{self._port}")
