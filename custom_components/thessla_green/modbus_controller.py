from pymodbus.client import ModbusTcpClient
import asyncio
import logging
import time

_LOGGER = logging.getLogger(__name__)

class ThesslaGreenModbusController:
    def __init__(self, host: str, port: int, slave_id: int, update_interval: int = 30):
        self._host = host
        self._port = port
        self._slave = slave_id
        self._update_interval = update_interval
        self._client = ModbusTcpClient(host=self._host, port=self._port)
        self._data_holding = {}
        self._data_input = {}
        self._data_coil = {}
        self._lock = asyncio.Lock()
        self._task = None

        self._error_count = 0
        self._max_errors = 5
        self._disabled = False
        self._connected = False
        self._log_suppressed = False

        self._last_update_timestamp = None
        self._last_update_interval = None

        self._holding_blocks = [
            (256, 2), (4192, 2), (4198, 1), (4208, 3), (4210, 1),
            (4224, 1), (4320, 1), (4387, 1),
            (8192, 2), (8208, 1), (8222, 2), (8330, 2), (8444, 1)
        ]
        self._input_blocks = [(16, 4), (22, 1)]
        self._coil_blocks = [(9, 3)]

    async def start(self):
        self._task = asyncio.create_task(self._scheduler())

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._client.close()

    async def _ensure_connected(self) -> bool:
        if self._disabled:
            return False

        was_connected = self._connected
        connected = self._client.connect()

        if connected:
            try:
                test = self._client.read_holding_registers(address=4387, count=1, slave=self._slave)
                if test and not test.isError():
                    if not was_connected:
                        _LOGGER.warning("Modbus reconnected successfully.")
                    self._connected = True
                    self._log_suppressed = False
                    return True
                else:
                    _LOGGER.debug("Modbus connect OK, but test read of register 4387 failed.")
            except Exception as e:
                _LOGGER.debug("Modbus test read of register 4387 raised exception: %s", e)

        _LOGGER.warning("Modbus connection failed. Resetting Modbus client...")
        self._connected = False
        try:
            self._client.close()
        except Exception as e:
            _LOGGER.debug("Exception while closing client: %s", e)

        await asyncio.sleep(1)
        self._client = ModbusTcpClient(host=self._host, port=self._port)
        return False

    async def _scheduler(self):
        retry_interval = 60

        while True:
            if self._disabled:
                _LOGGER.warning("Modbus polling is disabled. Trying to reconnect in %ds...", retry_interval)
                if await self._ensure_connected():
                    self._disabled = False
                    self._error_count = 0
                    _LOGGER.warning("Modbus reconnected successfully. Resuming normal operation.")
                else:
                    await asyncio.sleep(retry_interval)
                continue

            try:
                if not await self._ensure_connected():
                    raise ConnectionError("Initial connect failed")

                await self._update_all()
                self._error_count = 0

            except Exception as e:
                self._error_count += 1
                _LOGGER.debug("Scheduler error (%d/%d): %s", self._error_count, self._max_errors, e)

                self._client.close()
                await asyncio.sleep(2)
                self._client = ModbusTcpClient(host=self._host, port=self._port)

                if self._error_count >= self._max_errors:
                    self._disabled = True
                    _LOGGER.warning("Too many Modbus errors (%d). Going offline.", self._error_count)

            await asyncio.sleep(self._update_interval)

    async def _update_all(self):
        async with self._lock:
            if not await self._ensure_connected():
                raise ConnectionError(f"Could not connect to Modbus server at {self._host}:{self._port}")

            now = time.time()
            if self._last_update_timestamp is not None:
                self._last_update_interval = now - self._last_update_timestamp
            self._last_update_timestamp = now

            # Odczyt HOLDING
            for start, count in self._holding_blocks:
                rr = self._client.read_holding_registers(address=start, count=count, slave=self._slave)
                if not rr.isError():
                    for i, val in enumerate(rr.registers):
                        self._data_holding[start + i] = val
                else:
                    _LOGGER.warning("Error reading holding registers %s-%s", start, start + count - 1)

            # Odczyt INPUT
            for start, count in self._input_blocks:
                rr = self._client.read_input_registers(address=start, count=count, slave=self._slave)
                if not rr.isError():
                    for i, val in enumerate(rr.registers):
                        self._data_input[start + i] = val
                else:
                    _LOGGER.warning("Error reading input registers %s-%s", start, start + count - 1)

            # Odczyt COIL
            for start, count in self._coil_blocks:
                rr = self._client.read_coils(address=start, count=count, slave=self._slave)
                if not rr.isError():
                    for i, val in enumerate(rr.bits):
                        self._data_coil[start + i] = int(val)
                else:
                    _LOGGER.warning("Error reading coils %s-%s", start, start + count - 1)

    async def read_holding(self, address):
        async with self._lock:
            if self._disabled or not self._connected:
                if not self._log_suppressed:
                    _LOGGER.warning("Modbus offline, skipping read_holding")
                    self._log_suppressed = True
                return None
            self._log_suppressed = False
            return self._data_holding.get(address)

    async def read_input(self, address):
        async with self._lock:
            if self._disabled or not self._connected:
                if not self._log_suppressed:
                    _LOGGER.warning("Modbus offline, skipping read_input")
                    self._log_suppressed = True
                return None
            self._log_suppressed = False
            return self._data_input.get(address)

    async def write_register(self, address: int, value: int) -> bool:
        async with self._lock:
            if self._disabled or not self._connected:
                if not self._log_suppressed:
                    _LOGGER.error("Modbus offline, skipping write_register")
                    self._log_suppressed = True
                return False
            self._log_suppressed = False
            try:
                rr = self._client.write_register(address=address, value=value, slave=self._slave)
                if rr.isError():
                    _LOGGER.error("Modbus write error at address %s with value %s", address, value)
                    return False
                return True
            except Exception as e:
                _LOGGER.exception("Exception during Modbus write: %s", e)
                return False

    async def read_coil(self, address):
        async with self._lock:
            if self._disabled or not self._connected:
                if not self._log_suppressed:
                    _LOGGER.error("Modbus offline, skipping read_coil")
                    self._log_suppressed = True
                return None
            self._log_suppressed = False
            try:
                rr = self._client.read_coils(address=address, count=1, slave=self._slave)
                if rr.isError():
                    _LOGGER.error("Modbus coil read error at address %s", address)
                    return None
                return bool(rr.bits[0])
            except Exception as e:
                _LOGGER.exception("Exception during Modbus coil read: %s", e)
                return None

    async def get_last_update_interval(self) -> float | None:
        """Return time in seconds between last two Modbus full updates."""
        async with self._lock:
            return self._last_update_interval