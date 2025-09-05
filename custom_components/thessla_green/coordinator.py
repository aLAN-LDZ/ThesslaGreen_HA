import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .modbus_controller import ThesslaGreenModbusController, ControllerData

_LOGGER = logging.getLogger(__name__)


class ThesslaGreenCoordinator(DataUpdateCoordinator[ControllerData]):

    def __init__(self, hass, controller: ThesslaGreenModbusController, scan_interval: int):
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.controller = controller

    async def _async_update_data(self):
        try:
            return await self.controller.fetch_data()
        except Exception as err:
            raise UpdateFailed(f"Error fetching Modbus data: {err}") from err

    @property
    def safe_data(self) -> ControllerData:
        return self.data or ControllerData()
