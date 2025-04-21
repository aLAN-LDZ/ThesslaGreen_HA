from pymodbus.client.tcp import ModbusTcpClient
import logging

_LOGGER = logging.getLogger(__name__)


class ModbusController:
    def __init__(self, host: str, port: int, timeout: int = 5):
        self._client = ModbusTcpClient(host=host, port=port, timeout=timeout)
        self._host = host
        self._port = port

    def connect(self) -> bool:
        if not self._client.connect():
            _LOGGER.error(f"Failed to connect to Modbus server at {self._host}:{self._port}")
            return False
        return True

    def close(self):
        self._client.close()

    def ensure_connected(self) -> bool:
        """Ensure the Modbus client is connected. Reconnect if needed."""
        if not self._client.connected:
            _LOGGER.warning(f"Modbus client disconnected from {self._host}:{self._port}, attempting reconnect...")
            if not self._client.connect():
                _LOGGER.error(f"Reconnection to Modbus server at {self._host}:{self._port} failed")
                return False
            _LOGGER.info(f"Successfully reconnected to Modbus server at {self._host}:{self._port}")
        return True

    @property
    def client(self) -> ModbusTcpClient:
        return self._client

    def read_register(self, input_type: str, address: int, slave: int = 1) -> int | None:
        if not self.ensure_connected():
            return None
        try:
            if input_type == "input":
                rr = self._client.read_input_registers(address=address, count=1, slave=slave)
            else:
                rr = self._client.read_holding_registers(address=address, count=1, slave=slave)

            if rr.isError():
                _LOGGER.error(f"Modbus read error (type={input_type}) at address {address}")
                return None

            value = rr.registers[0]
            if value >= 0x8000:
                value -= 0x10000  # signed int16
            return value

        except Exception as e:
            _LOGGER.exception(f"Exception while reading Modbus register: {e}")
            return None

    def write_register(self, address: int, value: int, slave: int = 1) -> bool:
        if not self.ensure_connected():
            return None
        try:
            rr = self._client.write_register(address=address, value=value, slave=slave)
            if rr.isError():
                _LOGGER.error(f"Modbus write error at address {address} with value {value}")
                return False
            return True
        except Exception as e:
            _LOGGER.exception(f"Exception while writing Modbus register: {e}")
            return False

    def read_coil(self, address: int, slave: int = 1) -> bool | None:
        if not self.ensure_connected():
            return None
        try:
            rr = self._client.read_coils(address=address, count=1, slave=slave)
            if rr.isError():
                _LOGGER.error(f"Modbus coil read error at address {address}")
                return None
            return bool(rr.bits[0])
        except Exception as e:
            _LOGGER.exception(f"Exception while reading coil at {address}: {e}")
            return None

    def read_holding(self, address: int, slave: int = 1) -> int | None:
        if not self.ensure_connected():
            return None
        try:
            rr = self._client.read_holding_registers(address=address, count=1, slave=slave)
            if rr.isError():
                _LOGGER.error(f"Modbus holding register read error at address {address}")
                return None
            value = rr.registers[0]
            return value - 0x10000 if value >= 0x8000 else value
        except Exception as e:
            _LOGGER.exception(f"Exception while reading holding register at {address}: {e}")
            return None