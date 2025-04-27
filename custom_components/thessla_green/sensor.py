from __future__ import annotations
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfTemperature, UnitOfTime, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from . import DOMAIN
from .modbus_controller import ThesslaGreenModbusController
from .coordinator import ThesslaGreenCoordinator

_LOGGER = logging.getLogger(__name__)

SENSORS = [
    # Temperatura
    {"name": "Rekuperator Temperatura Czerpnia", "address": 16, "input_type": "input", "scale": 0.1, "precision": 1, "unit": UnitOfTemperature.CELSIUS, "icon": "mdi:thermometer"},
    {"name": "Rekuperator Temperatura Nawiew", "address": 17, "input_type": "input", "scale": 0.1, "precision": 1, "unit": UnitOfTemperature.CELSIUS, "icon": "mdi:thermometer"},
    {"name": "Rekuperator Temperatura Wywiew", "address": 18, "input_type": "input", "scale": 0.1, "precision": 1, "unit": UnitOfTemperature.CELSIUS, "icon": "mdi:thermometer"},
    {"name": "Rekuperator Temperatura za FPX", "address": 19, "input_type": "input", "scale": 0.1, "precision": 1, "unit": UnitOfTemperature.CELSIUS, "icon": "mdi:thermometer"},
    {"name": "Rekuperator Temperatura PCB", "address": 22, "input_type": "input", "scale": 0.1, "precision": 1, "unit": UnitOfTemperature.CELSIUS, "icon": "mdi:cpu-64-bit"},
    # Przepływy
    {"name": "Rekuperator Strumień nawiew", "address": 256, "input_type": "holding", "scale": 1, "precision": 1, "unit": "m3/h", "icon": "mdi:fan"},
    {"name": "Rekuperator Strumień wywiew", "address": 257, "input_type": "holding", "scale": 1, "precision": 1, "unit": "m3/h", "icon": "mdi:fan"},
    # Statusy i flagi
    {"name": "Rekuperator tryb pracy", "address": 4208, "input_type": "holding", "icon": "mdi:cog"},
    {"name": "Rekuperator speedmanual", "address": 4210, "input_type": "holding", "unit": "%", "icon": "mdi:speedometer"},
]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    modbus_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: ThesslaGreenCoordinator = modbus_data["coordinator"]
    slave = modbus_data["slave"]

    entities = [
        ModbusGenericSensor(coordinator=coordinator, slave=slave, **sensor)
        for sensor in SENSORS
    ]

    # Dodaj sensor diagnostyczny
    entities.append(ModbusUpdateIntervalSensor(coordinator=coordinator, slave=slave))

    async_add_entities(entities)

class ModbusGenericSensor(SensorEntity):
    """Representation of a standard Modbus sensor."""

    def __init__(self, coordinator: ThesslaGreenCoordinator, name, address, input_type="holding", scale=1.0, precision=0, unit=None, icon=None, slave=1):
        self.coordinator = coordinator
        self._address = address
        self._input_type = input_type
        self._scale = scale
        self._precision = precision
        self._unit = unit
        self._slave = slave
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_native_value = None
        self._attr_icon = icon
        self._attr_unique_id = f"thessla_sensor_{slave}_{address}"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{slave}")},
            "name": "Rekuperator Thessla",
            "manufacturer": "Thessla Green",
            "model": "Modbus Rekuperator",
        }

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def native_value(self):
        if self._input_type == "input":
            raw_value = self.coordinator.data["input"].get(self._address)
        else:
            raw_value = self.coordinator.data["holding"].get(self._address)

        if raw_value is None:
            return None

        value = raw_value * self._scale
        return round(value, self._precision)

    async def async_update(self):
        # Brak potrzeby ręcznego update — coordinator steruje
        pass

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

class ModbusUpdateIntervalSensor(SensorEntity):
    """Diagnostic sensor showing time between full Modbus updates."""

    def __init__(self, coordinator: ThesslaGreenCoordinator, slave: int):
        self.coordinator = coordinator
        self._slave = slave
        self._attr_name = "Modbus Update Interval"
        self._attr_native_unit_of_measurement = UnitOfTime.SECONDS
        self._attr_unique_id = f"thessla_update_interval_{slave}"
        self._attr_icon = "mdi:clock-time-eight"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{slave}")},
            "name": "Rekuperator Thessla",
            "manufacturer": "Thessla Green",
            "model": "Modbus Rekuperator",
        }

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def native_value(self):
        return round(self.coordinator.controller._last_update_interval, 1) if self.coordinator.controller._last_update_interval else None

    async def async_update(self):
        # Niepotrzebne — wszystko przez coordinator
        pass

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))