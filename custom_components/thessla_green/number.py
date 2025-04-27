from __future__ import annotations
import logging
from datetime import timedelta

from homeassistant.components.number import NumberEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from . import DOMAIN
from .modbus_controller import ThesslaGreenModbusController

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    modbus_data = hass.data[DOMAIN][entry.entry_id]
    controller: ThesslaGreenModbusController = modbus_data["controller"]
    slave = modbus_data["slave"]
    scan_interval = modbus_data["scan_interval"]

    async_add_entities([
        RekuperatorPredkoscNumber(controller=controller, slave=slave, scan_interval=scan_interval)
    ])


class RekuperatorPredkoscNumber(NumberEntity):
    def __init__(self, controller: ThesslaGreenModbusController, slave: int, scan_interval: int):
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
        self._attr_scan_interval = timedelta(seconds=scan_interval)

        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{slave}")},
            "name": "Rekuperator Thessla",
            "manufacturer": "Thessla Green",
            "model": "Modbus Rekuperator",
        }

    async def async_update(self):
        try:
            value = await self._controller.read_holding(self._address)
            if value is not None:
                self._attr_native_value = value
        except Exception as e:
            _LOGGER.exception(f"Exception during prędkość update: {e}")

    async def async_set_native_value(self, value: float) -> None:
        try:
            success = await self._controller.write_register(self._address, int(value))
            if success:
                self._attr_native_value = value
        except Exception as e:
            _LOGGER.exception(f"Exception during prędkość set: {e}")