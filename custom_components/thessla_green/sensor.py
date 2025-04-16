from homeassistant.components.sensor import SensorEntity
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from .const import DOMAIN

import random

async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities: AddEntitiesCallback) -> None:
    sensors = [
        ThesslaGreenSensor("Temperatura Czerpnia", "temp_czerpnia", TEMP_CELSIUS),
        ThesslaGreenSensor("Temperatura Nawiew", "temp_nawiew", TEMP_CELSIUS),
        ThesslaGreenSensor("Temperatura Wywiew", "temp_wywiew", TEMP_CELSIUS),
    ]
    async_add_entities(sensors, update_before_add=True)

class ThesslaGreenSensor(SensorEntity):
    def __init__(self, name: str, unique_id: str, unit: str) -> None:
        self._attr_name = name
        self._attr_unique_id = f"thessla_{unique_id}"
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = "measurement"
        self._attr_native_value = None

    async def async_update(self):
        # Tu potem pobierzemy wartość z Modbusa – teraz robimy udawaną temperaturę
        self._attr_native_value = round(random.uniform(18.0, 22.0), 1)
