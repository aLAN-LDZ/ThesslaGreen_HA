from __future__ import annotations
import logging
from datetime import timedelta  # <-- DODANE

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from . import DOMAIN
from .modbus_controller import ThesslaGreenModbusController

_LOGGER = logging.getLogger(__name__)

SWITCHES = [
    {"name": "Rekuperator bypass", "address": 4320, "command_on": 0, "command_off": 1, "verify": True},
    {"name": "Rekuperator ON/OFF", "address": 4387, "command_on": 1, "command_off": 0, "verify": True},
    {"name": "Rekuperator mode", "address": 4208, "command_on": 0, "command_off": 1, "verify": True},
]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    modbus_data = hass.data[DOMAIN][entry.entry_id]
    controller: ThesslaGreenModbusController = modbus_data["controller"]
    slave = modbus_data["slave"]
    scan_interval = modbus_data["scan_interval"]

    async_add_entities([
        ModbusSwitch(
            name=sw["name"],
            address=sw["address"],
            command_on=sw["command_on"],
            command_off=sw["command_off"],
            verify=sw.get("verify", False),
            controller=controller,
            slave=slave,
            scan_interval=scan_interval,
        ) for sw in SWITCHES
    ])


class ModbusSwitch(SwitchEntity):
    def __init__(self, name, address, command_on, command_off, verify, controller, slave, scan_interval):
        self._attr_name = name
        self._address = address
        self._command_on = command_on
        self._command_off = command_off
        self._verify = verify
        self._slave = slave
        self._controller = controller
        self._attr_is_on = False
        self._attr_unique_id = f"thessla_switch_{slave}_{self._address}"
        self._attr_scan_interval = timedelta(seconds=scan_interval)

        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{slave}")},
            "name": "Rekuperator Thessla",
            "manufacturer": "Thessla Green",
            "model": "Modbus Rekuperator",
        }

    async def async_turn_on(self, **kwargs):
        try:
            success = await self._controller.write_register(self._address, self._command_on)
            if success and not self._verify:
                self._attr_is_on = True
            elif self._verify:
                await self.async_update()
        except Exception as e:
            _LOGGER.exception(f"Error turning on {self._attr_name}: {e}")

    async def async_turn_off(self, **kwargs):
        try:
            success = await self._controller.write_register(self._address, self._command_off)
            if success and not self._verify:
                self._attr_is_on = False
            elif self._verify:
                await self.async_update()
        except Exception as e:
            _LOGGER.exception(f"Error turning off {self._attr_name}: {e}")

    async def async_update(self):
        if not self._verify:
            return
        try:
            value = await self._controller.read_holding(self._address)
            if value is not None:
                self._attr_is_on = (value == self._command_on)
        except Exception as e:
            _LOGGER.exception(f"Error verifying {self._attr_name}: {e}")