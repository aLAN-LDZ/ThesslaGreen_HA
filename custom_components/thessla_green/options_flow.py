import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.selector import selector

from .const import DOMAIN

# Czytelna etykieta w UI (bez strings.json)
DISPLAY_KEY = "Sensor poboru mocy (W lub kW)"
ACCEPTED_UNITS = {"W", "kW", "watt", "Watt", "KW"}  # dopuszczalne warianty

class ThesslaGreenOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow for Thessla Green integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        hass: HomeAssistant = self.hass
        errors = {}

        if user_input is not None:
            # pobierz wartość spod etykiety (bez strings.json używamy 'ładnego' klucza)
            entity_id = user_input.get(DISPLAY_KEY)

            if not entity_id:
                errors[DISPLAY_KEY] = "Wybierz sensor poboru mocy."
            else:
                st = hass.states.get(entity_id)
                unit = st and st.attributes.get("unit_of_measurement")
                if unit and unit not in ACCEPTED_UNITS:
                    errors[DISPLAY_KEY] = f"Nieobsługiwana jednostka: {unit}. Dozwolone: W lub kW."

            if not errors:
                # Zapisz pod standardową nazwą opcji
                return self.async_create_entry(
                    title="",
                    data={"sensor_power": entity_id},
                )

        # domyślna wartość do formularza (jeśli wcześniej zapisano)
        default_entity = self.config_entry.options.get("sensor_power")

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    DISPLAY_KEY,
                    default=default_entity
                ): selector({
                    "entity": {
                        "domain": "sensor",
                        # Preferencja dla sensorów mocy (nie blokuje innych):
                        "device_class": "power"
                    }
                }),
            }),
            errors=errors,
        )