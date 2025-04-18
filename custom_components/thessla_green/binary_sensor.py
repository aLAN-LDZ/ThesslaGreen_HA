from __future__ import annotations
import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from pymodbus.client.tcp import ModbusTcpClient
from . import DOMAIN

from datetime import timedelta

SCAN_INTERVAL = timedelta(seconds=10)

_LOGGER = logging.getLogger(__name__)

BINARY_SENSORS = [
    {"name": "Rekuperator Silownik bypassu", "address": 9},
    {"name": "Rekuperator Potwierdzenie pracy", "address": 11},
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    host = data["host"]
    port = data["port"]
    slave = data["slave"]

    async_add_entities([
        ModbusBinarySensor(
            name=sensor["name"],
            address=sensor["address"],
            host=host,
            port=port,
            slave=slave
        ) for sensor in BINARY_SENSORS
    ])


class ModbusBinarySensor(BinarySensorEntity):
    def __init__(self, name: str, address: int, host: str, port: int, slave: int):
        self._attr_name = name
        self._address = address
        self._slave = slave
        self._client = ModbusTcpClient(host, port=port, timeout=5)
        self._attr_is_on = None
        self._attr_unique_id = f"thessla_bin_{slave}_{address}"

    def update(self) -> None:
        try:
            self._client.connect()
            rr = self._client.read_discrete_inputs(address=self._address, count=1, slave=self._slave)
            if rr.isError():
                _LOGGER.error(f"Modbus read error for {self._attr_name}: {rr}")
                return

            # Inwersja logiki (jeśli 0 = ON, 1 = OFF)
            self._attr_is_on = not rr.bits[0]

        except Exception as e:
            _LOGGER.exception(f"Error reading binary sensor {self._attr_name}: {e}")
        finally:
            self._client.close()