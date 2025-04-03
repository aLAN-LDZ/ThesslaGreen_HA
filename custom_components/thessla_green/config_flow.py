import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from pymodbus.client.tcp import ModbusTcpClient
import logging
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class ThesslaGreenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Konfiguracja UI dla integracji Thessla Green."""

    async def async_step_user(self, user_input=None):
        """Pierwszy krok konfiguracji."""
        errors = {}

        if user_input is not None:
            host = user_input["host"]
            port = user_input["port"]

            # Sprawdzamy połączenie z Modbus
            if not await self.hass.async_add_executor_job(self._test_connection, host, port):
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title="Thessla Green", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("host"): str,
                vol.Required("port", default=502): int,
            }),
            errors=errors,
        )

    def _test_connection(self, host, port):
        """Testuje połączenie Modbus TCP."""
        try:
            client = ModbusTcpClient(host, port)
            connected = client.connect()
            client.close()
            return connected
        except Exception as e:
            _LOGGER.error(f"Błąd połączenia z Modbus TCP: {e}")
            return False
