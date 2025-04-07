from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

DOMAIN = "thessla_green"

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Setup z YAML (na razie nie używamy, bo robimy config w UI)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup z UI (dodamy później)."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Wyłączanie integracji."""
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
