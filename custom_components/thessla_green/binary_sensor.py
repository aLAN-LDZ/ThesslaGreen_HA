from __future__ import annotations
import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

BINARY_SENSORS = [
    # Odczyt z COILS
    {"name": "Rekuperator Silownik bypassu", "address": 9, "input_type": "coil", "icon_on": "mdi:valve-open", "icon_off": "mdi:valve-closed"},
    {"name": "Rekuperator Potwierdzenie pracy", "address": 11, "input_type": "coil", "icon_on": "mdi:check-circle", "icon_off": "mdi:circle-outline"},
    
    # Odczyt z HOLDING REGISTERS (przeniesione z sensor.py)
    {"name": "Rekuperator Alarm", "address": 8192, "input_type": "holding", "device_class": "problem"},
    {"name": "Rekuperator Awaria CF Nawiewu", "address": 8330, "input_type": "holding", "device_class": "problem"},
    {"name": "Rekuperator Awaria CF Wywiewu", "address": 8331, "input_type": "holding", "device_class": "problem"},
    {"name": "Rekuperator Awaria Wentylatora Nawiewu", "address": 8222, "input_type": "holding", "device_class": "problem"},
    {"name": "Rekuperator Awaria Wentylatora Wywiewu", "address": 8223, "input_type": "holding", "device_class": "problem"},
    {"name": "Rekuperator Bypass", "address": 4320, "input_type": "holding", "icon_on": "mdi:valve-open", "icon_off": "mdi:valve-closed"},
    {"name": "Rekuperator Error", "address": 8193, "input_type": "holding", "device_class": "problem"},
    {"name": "Rekuperator fpx flaga", "address": 4192, "input_type": "holding", "icon_on": "mdi:flag", "icon_off": "mdi:flag-outline"},
    {"name": "Rekuperator FPX tryb", "address": 4198, "input_type": "holding", "icon_on": "mdi:fan-alert", "icon_off": "mdi:fan"},
    {"name": "Rekuperator FPX zabezpieczenie termiczne", "address": 8208, "input_type": "holding", "device_class": "safety"},
    {"name": "Rekuperator lato zima", "address": 4209, "input_type": "holding", "icon_on": "mdi:sun-thermometer", "icon_off": "mdi:snowflake"},
    {"name": "Rekuperator Wymiana Filtrów", "address": 8444, "input_type": "holding", "icon_on": "mdi:air-filter", "icon_off": "mdi:air-filter-off"},
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
        ModbusBinarySensor(client=client, slave=slave, **sensor)
        for sensor in BINARY_SENSORS
    ])

class ModbusBinarySensor(BinarySensorEntity):
    """Representation of a binary Modbus sensor."""

    def __init__(self, name, address, input_type="coil", client=None, slave=1, device_class=None, icon_on=None, icon_off=None):
        self._attr_name = name
        self._address = address
        self._input_type = input_type
        self._client = client
        self._slave = slave
        self._attr_is_on = None
        self._attr_unique_id = f"thessla_binary_sensor_{slave}_{address}"
        self._attr_device_class = device_class
        self._icon_on = icon_on
        self._icon_off = icon_off

        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{slave}")},
            "name": "Rekuperator Thessla",
            "manufacturer": "Thessla Green",
            "model": "Modbus Rekuperator",
        }
    
    @property
    def icon(self) -> str | None:
        if self._attr_is_on is None:
            return None
        if self._attr_is_on and self._icon_on:
            return self._icon_on
        if not self._attr_is_on and self._icon_off:
            return self._icon_off
        return None

    def update(self) -> None:
        try:
            if self._input_type == "coil":
                rr = self._client.read_coils(address=self._address, count=1, slave=self._slave)
                if rr.isError():
                    _LOGGER.error(f"Modbus coil read error for {self._attr_name}: {rr}")
                    return
                self._attr_is_on = bool(rr.bits[0])

            elif self._input_type == "holding":
                rr = self._client.read_holding_registers(address=self._address, count=1, slave=self._slave)
                if rr.isError():
                    _LOGGER.error(f"Modbus holding register read error for {self._attr_name}: {rr}")
                    return
                self._attr_is_on = rr.registers[0] == 1

        except Exception as e:
            _LOGGER.exception(f"Error reading Modbus data: {e}")