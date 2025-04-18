"""Platform for sensor integration."""
from __future__ import annotations
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from . import DOMAIN

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
    {"name": "Rekuperator lato zima", "address": 4209, "input_type": "holding", "icon": "mdi:snowflake"},
    {"name": "Rekuperator Bypass", "address": 4320, "input_type": "holding", "icon": "mdi:valve"},
    {"name": "Rekuperator tryb pracy", "address": 4208, "input_type": "holding", "icon": "mdi:cog"},
    {"name": "Rekuperator speedmanual", "address": 4210, "input_type": "holding", "unit": "%", "icon": "mdi:speedometer"},
    {"name": "Rekuperator fpx flaga", "address": 4192, "input_type": "holding", "icon": "mdi:flag"},
    {"name": "Rekuperator FPX tryb", "address": 4198, "input_type": "holding", "icon": "mdi:fan-alert"},
    {"name": "Rekuperator Alarm", "address": 8192, "input_type": "holding", "icon": "mdi:alarm-light"},
    {"name": "Rekuperator Error", "address": 8193, "input_type": "holding", "icon": "mdi:alert-circle"},
    {"name": "Rekuperator FPX zabezpieczenie termiczne", "address": 8208, "input_type": "holding", "icon": "mdi:thermometer-alert"},
    {"name": "Rekuperator Awaria Wentylatora Nawiewu", "address": 8222, "input_type": "holding", "icon": "mdi:fan-off"},
    {"name": "Rekuperator Awaria Wentylatora Wywiewu", "address": 8223, "input_type": "holding", "icon": "mdi:fan-off"},
    {"name": "Rekuperator Awaria CF Nawiewu", "address": 8330, "input_type": "holding", "icon": "mdi:fan-alert"},
    {"name": "Rekuperator Awaria CF Wywiewu", "address": 8331, "input_type": "holding", "icon": "mdi:fan-alert"},
    {"name": "Rekuperator Wymiana Filtrów", "address": 8444, "input_type": "holding", "icon": "mdi:air-filter"},
]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    modbus_data = hass.data[DOMAIN][entry.entry_id]
    client = modbus_data["client"]
    slave = modbus_data["slave"]

    async_add_entities([
        ModbusGenericSensor(client=client, slave=slave, **sensor)
        for sensor in SENSORS
    ])

class ModbusGenericSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, name, address, input_type="holding", scale=1.0, precision=0, unit=None, icon=None, client=None, slave=1):
        self._attr_name = name
        self._address = address
        self._input_type = input_type
        self._scale = scale
        self._precision = precision
        self._unit = unit
        self._slave = slave
        self._attr_native_unit_of_measurement = unit
        self._client = client
        self._attr_native_value = None
        self._attr_icon = icon
        self._attr_unique_id = f"thessla_sensor_{slave}_{address}"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{slave}")},
            "name": "Rekuperator Thessla",
            "manufacturer": "Thessla Green",
            "model": "Modbus Rekuperator",
        }

    def update(self) -> None:
        try:
            if self._input_type == "input":
                rr = self._client.read_input_registers(address=self._address, count=1, slave=self._slave)
            else:
                rr = self._client.read_holding_registers(address=self._address, count=1, slave=self._slave)

            if rr.isError():
                _LOGGER.error(f"Modbus read error for {self._attr_name}: {rr}")
                return

            raw_value = rr.registers[0]
            if raw_value >= 0x8000:
                raw_value -= 0x10000  # convert to signed int16

            value = raw_value * self._scale
            self._attr_native_value = round(value, self._precision)

        except Exception as e:
            _LOGGER.exception(f"Error reading Modbus data: {e}")