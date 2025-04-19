from __future__ import annotations
import logging

from homeassistant.components.number import NumberEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType
from homeassistant.config_entries import ConfigEntry

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    modbus_data = hass.data[DOMAIN][entry.entry_id]
    client = modbus_data["client"]
    slave = modbus_data["slave"]

    async_add_entities([
        RekuperatorPredkoscNumber(client=client, slave=slave)
    ])


class RekuperatorPredkoscNumber(NumberEntity):
    def __init__(self, client, slave: int):
        self._attr_name = "Rekuperator Prędkość"
        self._address = 4210
        self._slave = slave
        self._client = client
        self._attr_native_unit_of_measurement = "%"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_native_value = None
        self._attr_unique_id = f"thessla_number_{slave}_{self._address}"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{slave}")},
            "name": "Rekuperator Thessla",
            "manufacturer": "Thessla Green",
            "model": "Modbus Rekuperator",
        }

    def update(self):
        try:
            rr = self._client.read_holding_registers(address=self._address, count=1, slave=self._slave)
            if rr.isError():
                _LOGGER.error(f"Error reading prędkość rekuperatora: {rr}")
                return

            self._attr_native_value = rr.registers[0]

        except Exception as e:
            _LOGGER.exception(f"Exception during prędkość update: {e}")

    def set_native_value(self, value: float) -> None:
        try:
            self._client.write_register(address=self._address, value=int(value), slave=self._slave)
            self._attr_native_value = value

        except Exception as e:
            _LOGGER.exception(f"Exception during prędkość set: {e}")