from pymodbus.client import AsyncModbusTcpClient
import logging

_LOGGER = logging.getLogger(__name__)

class ThesslaModbusHandler:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = AsyncModbusTcpClient(host=self.host, port=self.port)
        self.connected = False

    async def connect(self):
        """Nawiązuje połączenie z serwerem Modbus, jeśli nie jest jeszcze aktywne."""
        if not self.connected:
            await self.client.connect()
            self.connected = True
            _LOGGER.info("Połączono z Modbus TCP: %s:%s", self.host, self.port)

    async def read_input_register(self, address, count=1):
        """Odczytuje rejestry wejściowe z urządzenia Modbus."""
        if not self.connected:
            await self.connect()

        try:
            result = await self.client.read_input_registers(address=address, count=count)
            if result.isError():
                _LOGGER.warning("Błąd odczytu rejestru %s", address)
                return None
            return result.registers
        except Exception as e:
            _LOGGER.error("Wyjątek podczas odczytu Modbus: %s", e)
            return None