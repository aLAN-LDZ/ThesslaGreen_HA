from __future__ import annotations
import logging
from datetime import timedelta

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from . import DOMAIN
from .modbus_controller import ThesslaGreenModbusController

_LOGGER = logging.getLogger(__name__)

MODES = {
    "Brak trybu": 0,
    "Wietrzenie": 7,
    "Pusty Dom": 11,
    "Kominek": 2,
    "Okna": 10,
}

SEASONS = {
    "Lato": 0,
    "Zima": 1,
}

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
        RekuperatorTrybSelect(controller=controller, slave=slave, scan_interval=scan_interval),
        RekuperatorSezonSelect(controller=controller, slave=slave, scan_interval=scan_interval),
    ])


class RekuperatorTrybSelect(SelectEntity):
    def __init__(self, controller: ThesslaGreenModbusController, slave: int, scan_interval: int):
        self._attr_name = "Rekuperator Tryb"
        self._address = 4224
        self._slave = slave
        self._controller = controller
        self._attr_options = list(MODES.keys())
        self._attr_current_option = None
        self._value_map = {v: k for k, v in MODES.items()}
        self._attr_unique_id = f"thessla_select_{slave}_{self._address}"
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
                self._attr_current_option = self._value_map.get(value)
        except Exception as e:
            _LOGGER.exception(f"Exception during tryb update: {e}")

    async def async_select_option(self, option: str) -> None:
        try:
            code = MODES.get(option)
            if code is None:
                _LOGGER.error(f"Unknown option selected: {option}")
                return

            success = await self._controller.write_register(self._address, code)
            if success:
                self._attr_current_option = option

        except Exception as e:
            _LOGGER.exception(f"Exception during tryb selection: {e}")

class RekuperatorSezonSelect(SelectEntity):
    def __init__(self, controller: ThesslaGreenModbusController, slave: int, scan_interval: int):
        self._attr_name = "Rekuperator Sezon"
        self._address = 4209
        self._slave = slave
        self._controller = controller
        self._attr_options = list(SEASONS.keys())
        self._attr_current_option = None
        self._value_map = {v: k for k, v in SEASONS.items()}
        self._attr_unique_id = f"thessla_sezon_select_{slave}_{self._address}"
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
                self._attr_current_option = self._value_map.get(value)
        except Exception as e:
            _LOGGER.exception(f"Exception during sezon update: {e}")

    async def async_select_option(self, option: str) -> None:
        try:
            code = SEASONS.get(option)
            if code is None:
                _LOGGER.error(f"Unknown option selected: {option}")
                return

            success = await self._controller.write_register(self._address, code)
            if success:
                self._attr_current_option = option

        except Exception as e:
            _LOGGER.exception(f"Exception during sezon selection: {e}")