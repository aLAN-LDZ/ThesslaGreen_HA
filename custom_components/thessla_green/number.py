from __future__ import annotations
import logging

from homeassistant.components.number import NumberEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from . import DOMAIN
from .coordinator import ThesslaGreenCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities."""
    modbus_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: ThesslaGreenCoordinator = modbus_data["coordinator"]
    slave = modbus_data["slave"]

    async_add_entities([
        RekuperatorPredkoscNumber(coordinator=coordinator, slave=slave)
    ])


class RekuperatorPredkoscNumber(NumberEntity):
    """Representation of Rekuperator Prędkość as NumberEntity."""

    def __init__(self, coordinator: ThesslaGreenCoordinator, slave: int):
        self.coordinator = coordinator
        self._address = 4210
        self._slave = slave
        self._attr_name = "Rekuperator Prędkość"
        self._attr_native_unit_of_measurement = "%"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_unique_id = f"thessla_number_{slave}_{self._address}"

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
    def native_value(self) -> float | None:
        """Return the current speed value."""
        value = self.coordinator.data["holding"].get(self._address)
        if value is None:
            return None
        return value

    async def async_set_native_value(self, value: float) -> None:
        """Write speed value to the device."""
        try:
            success = await self.coordinator.controller.write_register(self._address, int(value))
            if success:
                await self.coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.exception(f"Exception during setting prędkość: {e}")

    async def async_update(self):
        """No-op, data provided by coordinator."""
        pass

    async def async_added_to_hass(self):
        """Register callbacks."""
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))