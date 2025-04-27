from __future__ import annotations
import logging

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from . import DOMAIN
from .coordinator import ThesslaGreenCoordinator

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
    """Set up select entities."""
    modbus_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: ThesslaGreenCoordinator = modbus_data["coordinator"]
    slave = modbus_data["slave"]

    async_add_entities([
        RekuperatorTrybSelect(coordinator=coordinator, slave=slave),
        RekuperatorSezonSelect(coordinator=coordinator, slave=slave),
    ])


class RekuperatorTrybSelect(SelectEntity):
    """Representation of Rekuperator Tryb Select."""

    def __init__(self, coordinator: ThesslaGreenCoordinator, slave: int):
        self.coordinator = coordinator
        self._address = 4224
        self._slave = slave
        self._attr_name = "Rekuperator Tryb"
        self._attr_options = list(MODES.keys())
        self._value_map = {v: k for k, v in MODES.items()}
        self._reverse_map = MODES
        self._attr_unique_id = f"thessla_select_{slave}_{self._address}"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{slave}")},
            "name": "Rekuperator Thessla",
            "manufacturer": "Thessla Green",
            "model": "Modbus Rekuperator",
        }

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        value = self.coordinator.data["holding"].get(self._address)
        if value is None:
            return None
        return self._value_map.get(value)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        try:
            code = self._reverse_map.get(option)
            if code is None:
                _LOGGER.error(f"Unknown option selected: {option}")
                return

            success = await self.coordinator.controller.write_register(self._address, code)
            if success:
                await self.coordinator.async_request_refresh()

        except Exception as e:
            _LOGGER.exception(f"Exception during tryb selection: {e}")

    async def async_update(self):
        """No-op, data provided by coordinator."""
        pass

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

class RekuperatorSezonSelect(SelectEntity):
    """Representation of Rekuperator Sezon Select."""

    def __init__(self, coordinator: ThesslaGreenCoordinator, slave: int):
        self.coordinator = coordinator
        self._address = 4209
        self._slave = slave
        self._attr_name = "Rekuperator Sezon"
        self._attr_options = list(SEASONS.keys())
        self._value_map = {v: k for k, v in SEASONS.items()}
        self._reverse_map = SEASONS
        self._attr_unique_id = f"thessla_sezon_select_{slave}_{self._address}"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{slave}")},
            "name": "Rekuperator Thessla",
            "manufacturer": "Thessla Green",
            "model": "Modbus Rekuperator",
        }

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        value = self.coordinator.data["holding"].get(self._address)
        if value is None:
            return None
        return self._value_map.get(value)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        try:
            code = self._reverse_map.get(option)
            if code is None:
                _LOGGER.error(f"Unknown option selected: {option}")
                return

            success = await self.coordinator.controller.write_register(self._address, code)
            if success:
                await self.coordinator.async_request_refresh()

        except Exception as e:
            _LOGGER.exception(f"Exception during sezon selection: {e}")

    async def async_update(self):
        """No-op, data provided by coordinator."""
        pass

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))