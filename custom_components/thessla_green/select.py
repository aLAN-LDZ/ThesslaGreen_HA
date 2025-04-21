from __future__ import annotations
import logging

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType

from . import DOMAIN
from .modbus_controller import ModbusController

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
    controller: ModbusController = modbus_data["controller"]
    slave = modbus_data["slave"]

    async_add_entities([
        RekuperatorTrybSelect(controller=controller, slave=slave),
        RekuperatorSezonSelect(controller=controller, slave=slave),
    ])


class RekuperatorTrybSelect(SelectEntity):
    def __init__(self, controller: ModbusController, slave: int):
        self._attr_name = "Rekuperator Tryb"
        self._address = 4224
        self._slave = slave
        self._controller = controller
        self._attr_options = list(MODES.keys())
        self._attr_current_option = None
        self._value_map = {v: k for k, v in MODES.items()}
        self._attr_unique_id = f"thessla_select_{slave}_{self._address}"

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
                self._attr_current_option = self._value_map.get(value)
        except Exception as e:
            _LOGGER.exception(f"Exception during tryb update: {e}")

    def select_option(self, option: str) -> None:
        try:
            code = MODES.get(option)
            if code is None:
                _LOGGER.error(f"Unknown option selected: {option}")
                return

            success = self._controller.write_register(self._address, code, self._slave)
            if success:
                self._attr_current_option = option

        except Exception as e:
            _LOGGER.exception(f"Exception during tryb selection: {e}")

class RekuperatorSezonSelect(SelectEntity):
    def __init__(self, controller: ModbusController, slave: int):
        self._attr_name = "Rekuperator Sezon"
        self._address = 4209
        self._slave = slave
        self._controller = controller
        self._attr_options = list(SEASONS.keys())
        self._attr_current_option = None
        self._value_map = {v: k for k, v in SEASONS.items()}
        self._attr_unique_id = f"thessla_sezon_select_{slave}_{self._address}"

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
                self._attr_current_option = self._value_map.get(value)
        except Exception as e:
            _LOGGER.exception(f"Exception during sezon update: {e}")

    def select_option(self, option: str) -> None:
        try:
            code = SEASONS.get(option)
            if code is None:
                _LOGGER.error(f"Unknown option selected: {option}")
                return

            success = self._controller.write_register(self._address, code, self._slave)
            if success:
                self._attr_current_option = option

        except Exception as e:
            _LOGGER.exception(f"Exception during sezon selection: {e}")