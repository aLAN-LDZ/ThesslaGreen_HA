from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from pymodbus.client.tcp import ModbusTcpClient
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "switch", "binary_sensor", "select", "number"]

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up from YAML (not used)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    host = entry.data["host"]
    port = entry.data["port"]
    slave = entry.data["slave"]

    # Tworzenie klienta Modbus i zapisanie w hass.data
    client = ModbusTcpClient(host=host, port=port, timeout=5)
    if not client.connect():
        _LOGGER.error("Cannot connect to Modbus server.")
        return False

    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "slave": slave,
    }

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = all(
        await hass.config_entries.async_forward_entry_unload(entry, platform)
        for platform in PLATFORMS
    )

    # Zamykanie połączenia Modbus
    client = hass.data[DOMAIN][entry.entry_id]["client"]
    client.close()

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok