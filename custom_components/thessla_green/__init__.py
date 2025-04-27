from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN, CONF_HOST, CONF_PORT, CONF_SLAVE, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
from .modbus_controller import ThesslaGreenModbusController
import logging


_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "switch", "binary_sensor", "select", "number"]

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up from YAML (not used)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    slave = entry.data[CONF_SLAVE]
    update_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    controller = ThesslaGreenModbusController(
        host=host,
        port=port,
        slave_id=slave,
        update_interval=update_interval
    )

    await controller.start()

    hass.data[DOMAIN][entry.entry_id] = {
        "controller": controller,
        "slave": slave,
        "scan_interval": update_interval,
    }

    for platform in PLATFORMS:
        await hass.config_entries.async_forward_entry_setup(entry, platform)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = all(
        await hass.config_entries.async_forward_entry_unload(entry, platform)
        for platform in PLATFORMS
    )

    controller: ThesslaGreenModbusController = hass.data[DOMAIN][entry.entry_id]["controller"]
    await controller.stop()

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok