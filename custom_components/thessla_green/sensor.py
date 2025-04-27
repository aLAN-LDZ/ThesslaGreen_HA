from __future__ import annotations
import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfTemperature, UnitOfTime, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from . import DOMAIN
from .modbus_controller import ThesslaGreenModbusController

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
    controller: ThesslaGreenModbusController = modbus_data["controller"]
    slave = modbus_data["slave"]
    scan_interval = modbus_data["scan_interval"]

    entities = [
        ModbusGenericSensor(controller=controller, slave=slave, scan_interval=scan_interval, **sensor)
        for sensor in SENSORS
    ]

    # Dodaj sensor diagnostyczny
    entities.append(ModbusUpdateIntervalSensor(controller=controller, slave=slave, scan_interval=scan_interval))

    async_add_entities(entities)

class ModbusGenericSensor(SensorEntity):
    """Representation of a standard Modbus sensor."""

    def __init__(self, name, address, input_type="holding", scale=1.0, precision=0, unit=None, icon=None, controller=None, slave=1, scan_interval=30):
        self._attr_name = name
        self._address = address
        self._input_type = input_type
        self._scale = scale
        self._precision = precision
        self._unit = unit
        self._slave = slave
        self._controller = controller
        self._attr_native_unit_of_measurement = unit
        self._attr_native_value = None
        self._attr_icon = icon
        self._attr_unique_id = f"thessla_sensor_{slave}_{address}"
        self._attr_scan_interval = timedelta(seconds=scan_interval)

        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{slave}")},
            "name": "Rekuperator Thessla",
            "manufacturer": "Thessla Green",
            "model": "Modbus Rekuperator",
        }

    async def async_update(self) -> None:
        try:
            if self._input_type == "input":
                raw_value = await self._controller.read_input(self._address)
            else:
                raw_value = await self._controller.read_holding(self._address)

            if raw_value is None:
                return

            value = raw_value * self._scale
            self._attr_native_value = round(value, self._precision)

        except Exception as e:
            _LOGGER.exception(f"Error in ModbusGenericSensor update: {e}")

class ModbusUpdateIntervalSensor(SensorEntity):
    """Diagnostic sensor showing time between full Modbus updates."""

    def __init__(self, controller: ThesslaGreenModbusController, slave: int, scan_interval: int):
        self._controller = controller
        self._slave = slave
        self._attr_name = "Modbus Update Interval"
        self._attr_native_unit_of_measurement = UnitOfTime.SECONDS
        self._attr_native_value = None
        self._attr_unique_id = f"thessla_update_interval_{slave}"
        self._attr_icon = "mdi:clock-time-eight"
        self._attr_scan_interval = timedelta(seconds=scan_interval)
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{slave}")},
            "name": "Rekuperator Thessla",
            "manufacturer": "Thessla Green",
            "model": "Modbus Rekuperator",
        }

    async def async_update(self):
        try:
            interval = await self._controller.get_last_update_interval()
            if interval is not None:
                self._attr_native_value = round(interval, 1)
        except Exception as e:
            _LOGGER.exception(f"Error reading update interval: {e}")