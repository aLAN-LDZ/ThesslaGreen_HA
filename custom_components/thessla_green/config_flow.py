import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from .const import DOMAIN

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
            return self.async_create_entry(title=user_input["name"], data=user_input)

        return self.async_show_form(step_id="user", data_schema=CONFIG_SCHEMA, errors=errors)
