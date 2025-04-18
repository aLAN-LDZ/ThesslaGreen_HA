from __future__ import annotations
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

SWITCHES = [
    {"name": "Rekuperator bypass", "address": 4320, "command_on": 0, "command_off": 1, "verify": True},
    {"name": "Rekuperator ON/OFF", "address": 4387, "command_on": 1, "command_off": 0, "verify": True},
    {"name": "Rekuperator mode", "address": 4208, "command_on": 0, "command_off": 1, "verify": True},
    {"name": "Rekuperator zima", "address": 4209, "command_on": 1, "command_off": 0, "verify": True},
]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    modbus_data = hass.data[DOMAIN][entry.entry_id]
    client = modbus_data["client"]
    slave = modbus_data["slave"]

    async_add_entities([
        ModbusSwitch(
            name=sw["name"],
            address=sw["address"],
            command_on=sw["command_on"],
            command_off=sw["command_off"],
            verify=sw.get("verify", False),
            client=client,
            slave=slave
        ) for sw in SWITCHES
    ])


class ModbusSwitch(SwitchEntity):
    def __init__(self, name, address, command_on, command_off, verify, client, slave):
        self._attr_name = name
        self._address = address
        self._command_on = command_on
        self._command_off = command_off
        self._verify = verify
        self._slave = slave
        self._attr_is_on = False
        self._client = client
        self._attr_unique_id = f"thessla_switch_{slave}_{self._address}"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{slave}")},
            "name": "Rekuperator Thessla",
            "manufacturer": "Thessla Green",
            "model": "Modbus Rekuperator",
        }

    def turn_on(self, **kwargs):
        try:
            self._client.write_register(address=self._address, value=self._command_on, slave=self._slave)
            if self._verify:
                self.update()
            else:
                self._attr_is_on = True
        except Exception as e:
            _LOGGER.exception(f"Error turning on {self._attr_name}: {e}")

    def turn_off(self, **kwargs):
        try:
            self._client.write_register(address=self._address, value=self._command_off, slave=self._slave)
            if self._verify:
                self.update()
            else:
                self._attr_is_on = False
        except Exception as e:
            _LOGGER.exception(f"Error turning off {self._attr_name}: {e}")

    def update(self):
        if not self._verify:
            return
        try:
            rr = self._client.read_holding_registers(address=self._address, count=1, slave=self._slave)
            if rr.isError():
                _LOGGER.error(f"Modbus read error (verify) for {self._attr_name}: {rr}")
                return
            self._attr_is_on = (rr.registers[0] == self._command_on)
        except Exception as e:
            _LOGGER.exception(f"Error verifying {self._attr_name}: {e}")