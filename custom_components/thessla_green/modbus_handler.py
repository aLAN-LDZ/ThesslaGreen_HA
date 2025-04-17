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

    async def read_input_register(self, address, count=1, unit=10):
        """Odczytuje rejestry wejściowe z urządzenia Modbus."""
        if not self.connected:
            await self.connect()

        try:
            result = await self.client.read_input_registers(address=address, count=count, unit=unit)
            if result.isError():
                _LOGGER.warning("Błąd odczytu rejestru %s", address)
                return None
            return result.registers
        except Exception as e:
            _LOGGER.error("Wyjątek podczas odczytu Modbus: %s", e)
            return None

    async def read_temperature(self, address):
        """Pomocnicza metoda do odczytu temperatury w formacie 0.1°C."""
        registers = await self.read_input_register(address)
        if registers and len(registers) > 0:
            value = registers[0]
            return value / 10.0
        else:
            _LOGGER.warning("Brak danych z rejestru temperatury %s", address)
            return None

    async def read_holding_register(self, address, count=1, unit=10):
        """Odczytuje holding rejestry z urządzenia Modbus."""
        if not self.connected:
            await self.connect()

        try:
            result = await self.client.read_holding_registers(address=address, count=count, unit=unit)
            if result.isError():
                _LOGGER.warning("Błąd odczytu holding rejestru %s", address)
                return None
            return result.registers
        except Exception as e:
            _LOGGER.error("Wyjątek podczas odczytu holding rejestru: %s", e)
            return None

    async def read_status(self, address, unit=10):
        """Sprawdza status urządzenia (np. dla binary_sensor)"""
        registers = await self.read_holding_register(address, count=1, unit=unit)
        if registers and len(registers) > 0:
            return registers[0] != 0  # Zwraca True/False na podstawie wartości rejestru
        else:
            _LOGGER.warning("Brak danych z rejestru statusu %s", address)
            return None