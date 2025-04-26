from __future__ import annotations
import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from . import DOMAIN
from .modbus_controller import ThesslaGreenModbusController

_LOGGER = logging.getLogger(__name__)

BINARY_SENSORS = [
    # Odczyt z COILS
    {"name": "Rekuperator Silownik bypassu", "address": 9, "input_type": "coil", "icon_on": "mdi:valve-open", "icon_off": "mdi:valve-closed"},
    {"name": "Rekuperator Potwierdzenie pracy", "address": 11, "input_type": "coil", "icon_on": "mdi:check-circle", "icon_off": "mdi:circle-outline"},
    
    # Odczyt z HOLDING REGISTERS
    {"name": "Rekuperator Alarm", "address": 8192, "input_type": "holding", "device_class": "problem"},
    {"name": "Rekuperator Awaria CF Nawiewu", "address": 8330, "input_type": "holding", "device_class": "problem"},
    {"name": "Rekuperator Awaria CF Wywiewu", "address": 8331, "input_type": "holding", "device_class": "problem"},
    {"name": "Rekuperator Awaria Wentylatora Nawiewu", "address": 8222, "input_type": "holding", "device_class": "problem"},
    {"name": "Rekuperator Awaria Wentylatora Wywiewu", "address": 8223, "input_type": "holding", "device_class": "problem"},
    {"name": "Rekuperator Bypass", "address": 4320, "input_type": "holding", "icon_on": "mdi:valve-open", "icon_off": "mdi:valve-closed"},
    {"name": "Rekuperator Error", "address": 8193, "input_type": "holding", "device_class": "problem"},
    {"name": "Rekuperator fpx flaga", "address": 4192, "input_type": "holding", "icon_on": "mdi:flag", "icon_off": "mdi:flag-outline"},
    {"name": "Rekuperator FPX tryb", "address": 4198, "input_type": "holding", "icon_on": "mdi:fan-alert", "icon_off": "mdi:fan"},
    {"name": "Rekuperator FPX zabezpieczenie termiczne", "address": 8208, "input_type": "holding", "device_class": "safety"},
    {"name": "Rekuperator lato zima", "address": 4209, "input_type": "holding", "icon_on": "mdi:sun-thermometer", "icon_off": "mdi:snowflake"},
    {"name": "Rekuperator Wymiana Filtrów", "address": 8444, "input_type": "holding", "icon_on": "mdi:air-filter", "icon_off": "mdi:fan-alert"},
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    modbus_data = hass.data[DOMAIN][entry.entry_id]
    controller: ThesslaGreenModbusController = modbus_data["controller"]
    slave = modbus_data["slave"]

    async_add_entities([
        ModbusBinarySensor(controller=controller, slave=slave, **sensor)
        for sensor in BINARY_SENSORS
    ])


class ModbusBinarySensor(BinarySensorEntity):
    def __init__(
        self,
        name: str,
        address: int,
        input_type: str = "coil",
        controller: ThesslaGreenModbusController = None,
        slave: int = 1,
        device_class: str | None = None,
        icon_on: str | None = None,
        icon_off: str | None = None,
    ):
        self._attr_name = name
        self._address = address
        self._input_type = input_type
        self._controller = controller
        self._slave = slave
        self._attr_is_on = None
        self._attr_unique_id = f"thessla_binary_sensor_{slave}_{address}"
        self._attr_device_class = device_class
        self._icon_on = icon_on
        self._icon_off = icon_off

        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{slave}")},
            "name": "Rekuperator Thessla",
            "manufacturer": "Thessla Green",
            "model": "Modbus Rekuperator",
        }
    
    @property
    def icon(self) -> str | None:
        if self._attr_is_on is None:
            return None
        return self._icon_on if self._attr_is_on else self._icon_off

    async def async_update(self) -> None:
        try:
            value: bool | None = None
            if self._input_type == "coil":
                value = await self._controller.read_coil(self._address)
            elif self._input_type == "holding":
                holding = await self._controller.read_holding(self._address)
                if holding is not None:
                    value = holding == 1
            else:
                _LOGGER.error(f"Unknown input_type '{self._input_type}' for {self._attr_name}")
                return

            if value is not None:
                self._attr_is_on = value

        except Exception as e:
            _LOGGER.exception(f"Error updating binary sensor {self._attr_name}: {e}")