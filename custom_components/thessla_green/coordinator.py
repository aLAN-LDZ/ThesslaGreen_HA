# coordinator.py

import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .modbus_controller import ThesslaGreenModbusController

_LOGGER = logging.getLogger(__name__)

class ThesslaGreenCoordinator(DataUpdateCoordinator):
    """Coordinator to manage data update for Thessla Green Modbus."""

    def __init__(self, hass, controller: ThesslaGreenModbusController, scan_interval: int):
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.controller = controller

    async def _async_update_data(self):
        """Fetch data from Modbus."""
        try:
            if not await self.controller._ensure_connected():
                raise UpdateFailed("Not connected to Modbus controller.")

            return {
                "holding": self.controller._data_holding.copy(),
                "input": self.controller._data_input.copy(),
            }
        except Exception as err:
            raise UpdateFailed(f"Error fetching Modbus data: {err}") from err