import asyncio
import logging
import time
from pymodbus import ModbusException
from pymodbus.client import AsyncModbusTcpClient

_LOGGER = logging.getLogger(__name__)

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
        self._connection_lock = asyncio.Lock()
        self._read_write_lock = asyncio.Lock()
        self._task: asyncio.Task | None = None

        self._data_holding: dict[int, int] = {}
        self._data_input: dict[int, int] = {}
        self._data_coil: dict[int, bool] = {}

        self._last_update_timestamp: float | None = None
        self._last_update_interval: float | None = None

        self._holding_blocks = [
            (256, 2), (4192, 2), (4198, 1), (4208, 3), (4210, 1),
            (4224, 1), (4320, 1), (4387, 1),
            (8192, 2), (8208, 1), (8222, 2), (8330, 2), (8444, 1)
        ]
        self._input_blocks = [(16, 4), (22, 1)]
        self._coil_blocks = [(9, 3)]

    def start(self):
        if not self._task:
            _LOGGER.info("Starting Modbus update loop for %s:%d (slave=%d, interval=%ds)", self._host, self._port, self._slave, self._update_interval)
            self._task = asyncio.create_task(self._update_loop())
        else:
            _LOGGER.warning("Update loop already running for %s:%d", self._host, self._port)

    async def stop(self):
        _LOGGER.info("Stopping Modbus controller for %s:%d", self._host, self._port)
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                _LOGGER.debug("Modbus update loop cancelled successfully")
            self._task = None
            self._client.close()

    async def ensure_connected(self) -> bool:
        async with self._connection_lock:
            if self._client.connected:
                return True

            _LOGGER.info("Attempting connection to Modbus server %s:%d", self._host, self._port)
            try:
                if await self._client.connect():
                    _LOGGER.info("Successfully connected to Modbus server %s:%d", self._host, self._port)
                    return True
                _LOGGER.warning("Failed to connect to Modbus server %s:%d", self._host, self._port)
            except Exception as exception:
                _LOGGER.exception("Exception during Modbus connection to %s:%d: %s", self._host, self._port, exception)

            return False

    async def _update_loop(self):
        _LOGGER.info("Modbus update loop started (interval=%ds)", self._update_interval)
        while True:
            try:
                if await self.ensure_connected():
                    await self._read_all_registers()
            except ModbusException as exception:
                _LOGGER.exception("ModbusException in update loop: %s", exception)

            await asyncio.sleep(self._update_interval)

    async def _read_all_registers(self):
        async with self._read_write_lock:
            now = time.time()
            if self._last_update_timestamp:
                self._last_update_interval = now - self._last_update_timestamp
                _LOGGER.debug("Time since last update: %.2f seconds", self._last_update_interval)
            self._last_update_timestamp = now

            _LOGGER.debug("Reading all register blocks for slave %d", self._slave)

            # Read holding registers
            for start, count in self._holding_blocks:
                try:
                    result = await self._client.read_holding_registers(address=start, count=count, device_id=self._slave)
                    if result.isError():
                        _LOGGER.warning("Error reading holding registers %d-%d", start, start + count - 1)
                        continue
                    for i, val in enumerate(result.registers):
                        self._data_holding[start + i] = val
                    _LOGGER.debug("Holding registers %d-%d read: %s", start, start + count - 1, result.registers)
                except Exception as e:
                    _LOGGER.exception("Exception reading holding registers %d-%d: %s", start, start + count - 1, e)

            # Read input registers
            for start, count in self._input_blocks:
                try:
                    result = await self._client.read_input_registers(address=start, count=count, device_id=self._slave)
                    if result.isError():
                        _LOGGER.warning("Error reading input registers %d-%d", start, start + count - 1)
                        continue
                    for i, val in enumerate(result.registers):
                        self._data_input[start + i] = val
                    _LOGGER.debug("Input registers %d-%d read: %s", start, start + count - 1, result.registers)
                except Exception as e:
                    _LOGGER.exception("Exception reading input registers %d-%d: %s", start, start + count - 1, e)

            # Read coils
            for start, count in self._coil_blocks:
                try:
                    result = await self._client.read_coils(address=start, count=count, device_id=self._slave)
                    if result.isError():
                        _LOGGER.warning("Error reading coils %d-%d", start, start + count - 1)
                        continue
                    for i, val in enumerate(result.bits):
                        self._data_coil[start + i] = bool(val)
                    _LOGGER.debug("Coils %d-%d read: %s", start, start + count - 1, result.bits)
                except Exception as e:
                    _LOGGER.exception("Exception reading coils %d-%d: %s", start, start + count - 1, e)

    async def write_register(self, address: int, value: int) -> bool:
        if not await self.ensure_connected():
            _LOGGER.error("Cannot write to register %d: Modbus offline", address)
            return False

        async with self._read_write_lock:
            try:
                _LOGGER.debug("Writing register %d = %s (slave=%d)", address, value, self._slave)
                result = await self._client.write_register(address=address, value=value, device_id=self._slave)
                if result.isError():
                    _LOGGER.error("Failed to write register %d with value %s", address, value)
                    return False
                _LOGGER.info("Successfully wrote register %d = %s", address, value)
                return True
            except Exception as e:
                _LOGGER.exception("Exception writing register %d = %s: %s", address, value, e)
                return False
