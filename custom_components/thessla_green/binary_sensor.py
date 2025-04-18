from __future__ import annotations
import logging
from datetime import timedelta

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

    entities = [
        ModbusBinarySensor(
            name=sensor["name"],
            address=sensor["address"],
            client=client,
            slave=slave,
        ) for sensor in BINARY_SENSORS
    ]

    async_add_entities(entities, update_before_add=True)

class ModbusBinarySensor(BinarySensorEntity):
    _attr_should_poll = True

    def __init__(self, name: str, address: int, client, slave: int):
        self._attr_name = name
        self._address = address
        self._slave = slave
        self._client = client
        self._attr_is_on = None
        self._attr_unique_id = f"thessla_bin_{slave}_{address}"

    async def async_update(self) -> None:
        _LOGGER.info(f"Updating binary sensor: {self._attr_name}")
        try:
            rr = self._client.read_discrete_inputs(address=self._address, count=1, slave=self._slave)
            if rr.isError():
                _LOGGER.error(f"Modbus read error for {self._attr_name}: {rr}")
                return

            self._attr_is_on = not rr.bits[0]

        except Exception as e:
            _LOGGER.exception(f"Error reading binary sensor {self._attr_name}: {e}")