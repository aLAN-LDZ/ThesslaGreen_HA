from __future__ import annotations
import logging

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

MODES = {
    "Brak trybu": 0,
    "Wietrzenie": 7,
    "Pusty Dom": 11,
    "Kominek": 2,
    "Okna": 10,
}

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    modbus_data = hass.data[DOMAIN][entry.entry_id]
    client = modbus_data["client"]
    slave = modbus_data["slave"]

    async_add_entities([
        RekuperatorTrybSelect(client=client, slave=slave)
    ])


class RekuperatorTrybSelect(SelectEntity):
    def __init__(self, client, slave: int):
        self._attr_name = "Rekuperator Tryb"
        self._address = 4224
        self._slave = slave
        self._client = client
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
            rr = self._client.read_holding_registers(address=self._address, count=1, slave=self._slave)
            if rr.isError():
                _LOGGER.error(f"Error reading rekuperator tryb: {rr}")
                return

            raw_value = rr.registers[0]
            self._attr_current_option = self._value_map.get(raw_value)

        except Exception as e:
            _LOGGER.exception(f"Exception during tryb update: {e}")

    def select_option(self, option: str) -> None:
        try:
            code = MODES.get(option)
            if code is None:
                _LOGGER.error(f"Unknown option selected: {option}")
                return

            self._client.write_register(address=self._address, value=code, slave=self._slave)
            self._attr_current_option = option

        except Exception as e:
            _LOGGER.exception(f"Exception during tryb selection: {e}")
