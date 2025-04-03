import voluptuous as vol
from homeassistant import config_entries
from pymodbus.client import ModbusTcpClient
import logging
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Schemat konfiguracji – użytkownik poda adres IP, port i nazwę
CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required("host"): str,
        vol.Required("port", default=9999): int,
        vol.Required("name", default="Rekuperator"): str,
    }
)

class ThesslaGreenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Konfiguracja UI dla integracji Thessla Green"""

    async def async_step_user(self, user_input=None):
        """Pierwszy krok konfiguracji."""
        errors = {}

        if user_input is not None:
            host = user_input["host"]
            port = user_input["port"]

            try:
                is_connected = await self.hass.async_add_executor_job(self._test_connection, host, port)
                if not is_connected:
                    errors["base"] = "cannot_connect"
                else:
                    return self.async_create_entry(title=user_input["name"], data=user_input)

            except Exception as e:
                _LOGGER.error(f"Nieoczekiwany błąd połączenia: {e}")
                errors["base"] = "unknown"

        return self.async_show_form(step_id="user", data_schema=CONFIG_SCHEMA, errors=errors)

    def _test_connection(self, host, port):
        """Test połączenia z Modbus TCP."""
        try:
            client = ModbusTcpClient(host=host, port=port)
            connected = client.connect()
            if not connected:
                _LOGGER.warning(f"Nie udało się połączyć z urządzeniem {host}:{port}")
            client.close()
            return connected
        except Exception as e:
            _LOGGER.error(f"Błąd połączenia z {host}:{port}: {e}")
            return False