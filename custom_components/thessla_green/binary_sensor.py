from __future__ import annotations
import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

BINARY_SENSORS = [
    {"name": "Rekuperator Silownik bypassu", "address": 9},
    {"name": "Rekuperator Potwierdzenie pracy", "address": 11},
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
        ModbusBinarySensor(name=sensor["name"], address=sensor["address"], client=client, slave=slave)
        for sensor in BINARY_SENSORS
    ])

class ModbusBinarySensor(BinarySensorEntity):
    """Representation of a binary Modbus sensor."""

    def __init__(self, name, address, client=None, slave=1):
        self._attr_name = name
        self._address = address
        self._client = client
        self._slave = slave
        self._attr_is_on = None
        self._attr_unique_id = f"thessla_binary_sensor_{slave}_{address}"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{slave}")},
            "name": "Rekuperator Thessla",
            "manufacturer": "Thessla Green",
            "model": "Modbus Rekuperator",
        }

    def update(self) -> None:
        try:
            rr = self._client.read_coils(address=self._address, count=1, slave=self._slave)

            if rr.isError():
                _LOGGER.error(f"Modbus coil read error for {self._attr_name}: {rr}")
                return

            self._attr_is_on = bool(rr.bits[0])

        except Exception as e:
            _LOGGER.exception(f"Error reading Modbus coil data: {e}")