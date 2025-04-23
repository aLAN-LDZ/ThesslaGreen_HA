from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusIOException
import asyncio
import logging

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
        self._lock = asyncio.Lock()
        self._task = None

        self._error_count = 0
        self._max_errors = 5
        self._disabled = False

        self._holding_blocks = [
            (256, 2), (4192, 2), (4198, 1), (4208, 3), (4210, 1),
            (4224, 1), (4320, 1), (4387, 1),
            (8192, 2), (8208, 1), (8222, 2), (8330, 2), (8444, 1)
        ]
        self._input_blocks = [(16, 4), (22, 1)]

    async def start(self):
        self._task = asyncio.create_task(self._scheduler())

    async def stop(self):
        if self._task:
            self._task.cancel()
        self._client.close()

    async def _scheduler(self):
        while True:
            if self._disabled:
                _LOGGER.error("Modbus polling disabled after %d consecutive errors", self._max_errors)
                return

            try:
                await self._update_all()
                self._error_count = 0  # reset po sukcesie
            except Exception as e:
                self._error_count += 1
                _LOGGER.error("Scheduler error (%d/%d): %s", self._error_count, self._max_errors, e)

                # Zamknij i spróbuj ponownie połączenie
                self._client.close()
                await asyncio.sleep(2)
                self._client = ModbusTcpClient(host=self._host, port=self._port)

                if self._error_count >= self._max_errors:
                    self._disabled = True
                    _LOGGER.error("Too many Modbus errors. Stopping further attempts.")

            await asyncio.sleep(self._update_interval)

    async def _update_all(self):
        async with self._lock:
            if not self._client.connect():
                raise ConnectionError(f"Could not connect to Modbus server at {self._host}:{self._port}")

            for start, count in self._holding_blocks:
                rr = self._client.read_holding_registers(address=start, count=count, slave=self._slave)
                if not rr.isError():
                    for i, val in enumerate(rr.registers):
                        self._data_holding[start + i] = val
                else:
                    _LOGGER.warning("Error reading holding registers %s-%s", start, start + count - 1)

            for start, count in self._input_blocks:
                rr = self._client.read_input_registers(address=start, count=count, slave=self._slave)
                if not rr.isError():
                    for i, val in enumerate(rr.registers):
                        self._data_input[start + i] = val
                else:
                    _LOGGER.warning("Error reading input registers %s-%s", start, start + count - 1)

    async def read_holding(self, address):
        async with self._lock:
            return self._data_holding.get(address)

    async def read_input(self, address):
        async with self._lock:
            return self._data_input.get(address)

    async def write_register(self, address: int, value: int) -> bool:
        async with self._lock:
            if not self._client.connect():
                _LOGGER.error("Could not connect to Modbus server for writing")
                return False
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
            if not self._client.connect():
                _LOGGER.error("Could not connect to Modbus server for coil read")
                return None
            try:
                rr = self._client.read_coils(address=address, count=1, slave=self._slave)
                if rr.isError():
                    _LOGGER.error("Modbus coil read error at address %s", address)
                    return None
                return bool(rr.bits[0])
            except Exception as e:
                _LOGGER.exception("Exception during Modbus coil read: %s", e)
                return None