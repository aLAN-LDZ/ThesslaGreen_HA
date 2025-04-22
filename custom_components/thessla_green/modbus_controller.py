from pymodbus.client.tcp import ModbusTcpClient
from pymodbus.exceptions import ModbusIOException
import time
import errno
import logging

_LOGGER = logging.getLogger(__name__)


class ModbusController:
    def __init__(self, host: str, port: int, timeout: int = 5):
        self._client = ModbusTcpClient(host=host, port=port, timeout=timeout)
        self._host = host
        self._port = port
        self._last_read_time = {}  # (type, address, slave): timestamp
        self._throttle_ttl = 30.0   # sekundy – minimalny odstęp czasu między odczytami

    def connect(self) -> bool:
        if not self._client.connect():
            _LOGGER.error(f"Failed to connect to Modbus server at {self._host}:{self._port}")
            return False
        return True

    def close(self):
        self._client.close()

    def ensure_connected(self) -> bool:
        if not self._client.connected:
            _LOGGER.warning(f"Modbus client disconnected from {self._host}:{self._port}, attempting reconnect...")
            self._client.close()
            self._client = ModbusTcpClient(host=self._host, port=self._port)  # odtwórz klienta na nowo
            if not self._client.connect():
                _LOGGER.error(f"Reconnection to Modbus server at {self._host}:{self._port} failed")
                return False
            _LOGGER.info(f"Successfully reconnected to Modbus server at {self._host}:{self._port}")
        return True

    @property
    def client(self) -> ModbusTcpClient:
        return self._client

    def _throttled(self, key: tuple) -> bool:
        now = time.time()
        last_time = self._last_read_time.get(key, 0)
        if now - last_time < self._throttle_ttl:
            return True
        self._last_read_time[key] = now
        return False

    def _safe_modbus_call(self, func, *args, **kwargs):
        """Executes a Modbus function with automatic reconnection retry on connection errors."""
        if not self.ensure_connected():
            return None

        try:
            return func(*args, **kwargs)

        except (BrokenPipeError, ConnectionResetError, ModbusIOException, OSError) as e:
            if isinstance(e, OSError) and e.errno not in (errno.EPIPE, errno.ECONNRESET, errno.EBADF):
                raise

            _LOGGER.warning(f"Connection lost or timeout: {e}. Reconnecting and retrying...")
            self._client.close()
            self._client = ModbusTcpClient(host=self._host, port=self._port)
            if self._client.connect():
                try:
                    return func(*args, **kwargs)
                except Exception as e2:
                    _LOGGER.exception(f"Retry failed after reconnect: {e2}")
            else:
                _LOGGER.error("Reconnect failed.")

        except Exception as e:
            _LOGGER.exception(f"Unexpected exception during Modbus operation: {e}")

        return None

    def read_register(self, input_type: str, address: int, slave: int = 1) -> int | None:
        key = (input_type, address, slave)
        if self._throttled(key):
            return None

        def read():
            if input_type == "input":
                return self._client.read_input_registers(address=address, count=1, slave=slave)
            return self._client.read_holding_registers(address=address, count=1, slave=slave)

        rr = self._safe_modbus_call(read)
        if rr is None or rr.isError():
            _LOGGER.error(f"Modbus read error (type={input_type}) at address {address}")
            return None

        value = rr.registers[0]
        return value - 0x10000 if value >= 0x8000 else value

    def read_holding(self, address: int, slave: int = 1) -> int | None:
        key = ("holding", address, slave)
        if self._throttled(key):
            return None

        def read():
            return self._client.read_holding_registers(address=address, count=1, slave=slave)

        rr = self._safe_modbus_call(read)
        if rr is None or rr.isError():
            _LOGGER.error(f"Modbus holding register read error at address {address}")
            return None

        value = rr.registers[0]
        return value - 0x10000 if value >= 0x8000 else value

    def read_coil(self, address: int, slave: int = 1) -> bool | None:
        def read():
            return self._client.read_coils(address=address, count=1, slave=slave)

        rr = self._safe_modbus_call(read)
        if rr is None or rr.isError():
            _LOGGER.error(f"Modbus coil read error at address {address}")
            return None

        return bool(rr.bits[0])

    def write_register(self, address: int, value: int, slave: int = 1) -> bool:
        def write():
            return self._client.write_register(address=address, value=value, slave=slave)

        rr = self._safe_modbus_call(write)
        if rr is None or rr.isError():
            _LOGGER.error(f"Modbus write error at address {address} with value {value}")
            return False

        return True