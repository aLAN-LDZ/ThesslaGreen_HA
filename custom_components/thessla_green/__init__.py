from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .modbus_handler import ThesslaModbusHandler
from .const import DOMAIN

PLATFORMS = ["sensor"]

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Setup z YAML (na razie nie używamy, bo robimy config w UI)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup z UI."""
    hass.data.setdefault(DOMAIN, {})

    host = entry.data["host"]
    port = entry.data["port"]

    # Utwórz klienta modbus i zapisz do hass.data
    modbus_client = ThesslaModbusHandler(host, port)
    await modbus_client.connect()

    hass.data[DOMAIN][entry.entry_id] = modbus_client

    # Przekaż integrację do platform
    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Wyłączanie integracji."""
    modbus_client = hass.data[DOMAIN].get(entry.entry_id, {}).get("client")
    if modbus_client:
        # Zakończenie połączenia Modbus
        await modbus_client.client.close()
    
    unload_ok = all([
        await hass.config_entries.async_forward_entry_unload(entry, platform)
        for platform in PLATFORMS
    ])

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok
