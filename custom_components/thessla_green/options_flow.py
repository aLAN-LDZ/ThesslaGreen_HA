import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.selector import selector
from .const import DOMAIN

class ThesslaGreenOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow for Thessla Green integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    "sensor_power",
                    default=self.config_entry.options.get("sensor_power")
                ): selector({"entity": {"domain": "sensor"}}),
            })
        )