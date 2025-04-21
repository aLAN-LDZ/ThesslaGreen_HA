from __future__ import annotations
import logging

from homeassistant.components.number import NumberEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType
from homeassistant.config_entries import ConfigEntry

from . import DOMAIN
from .modbus_controller import ModbusController

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    modbus_data = hass.data[DOMAIN][entry.entry_id]
    controller: ModbusController = modbus_data["controller"]
    slave = modbus_data["slave"]

    async_add_entities([
        RekuperatorPredkoscNumber(controller=controller, slave=slave)
    ])



class RekuperatorPredkoscNumber(NumberEntity):
    def __init__(self, controller: ModbusController, slave: int):
        self._attr_name = "Rekuperator Prędkość"
        self._address = 4210
        self._slave = slave
        self._controller = controller
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
            value = self._controller.read_register("holding", self._address, self._slave)
            if value is not None:
                self._attr_native_value = value
        except Exception as e:
            _LOGGER.exception(f"Exception during prędkość update: {e}")

    def set_native_value(self, value: float) -> None:
        try:
            success = self._controller.write_register(self._address, int(value), self._slave)
            if success:
                self._attr_native_value = value
        except Exception as e:
            _LOGGER.exception(f"Exception during prędkość set: {e}")