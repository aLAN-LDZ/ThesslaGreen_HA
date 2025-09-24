from __future__ import annotations
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfTemperature, UnitOfTime, EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_state_change_event

from . import DOMAIN
from .modbus_controller import ThesslaGreenModbusController
from .coordinator import ThesslaGreenCoordinator

_LOGGER = logging.getLogger(__name__)

SENSORS = [
    # Temperatura
    {"name": "Rekuperator Temperatura Czerpnia", "address": 16, "input_type": "input", "scale": 0.1, "precision": 1, "unit": UnitOfTemperature.CELSIUS, "icon": "mdi:thermometer"},
    {"name": "Rekuperator Temperatura Nawiew", "address": 17, "input_type": "input", "scale": 0.1, "precision": 1, "unit": UnitOfTemperature.CELSIUS, "icon": "mdi:thermometer"},
    {"name": "Rekuperator Temperatura Wywiew", "address": 18, "input_type": "input", "scale": 0.1, "precision": 1, "unit": UnitOfTemperature.CELSIUS, "icon": "mdi:thermometer"},
    {"name": "Rekuperator Temperatura za FPX", "address": 19, "input_type": "input", "scale": 0.1, "precision": 1, "unit": UnitOfTemperature.CELSIUS, "icon": "mdi:thermometer"},
    {"name": "Rekuperator Temperatura PCB", "address": 22, "input_type": "input", "scale": 0.1, "precision": 1, "unit": UnitOfTemperature.CELSIUS, "icon": "mdi:cpu-64-bit"},
    # Przepływy
    {"name": "Rekuperator Strumień nawiew", "address": 256, "input_type": "holding", "scale": 1, "precision": 1, "unit": "m3/h", "icon": "mdi:fan"},
    {"name": "Rekuperator Strumień wywiew", "address": 257, "input_type": "holding", "scale": 1, "precision": 1, "unit": "m3/h", "icon": "mdi:fan"},
    # Statusy i flagi
    {"name": "Rekuperator tryb pracy", "address": 4208, "input_type": "holding", "icon": "mdi:cog"},
    {"name": "Rekuperator speedmanual", "address": 4210, "input_type": "holding", "unit": "%", "icon": "mdi:speedometer"},
]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    modbus_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: ThesslaGreenCoordinator = modbus_data["coordinator"]
    slave = modbus_data["slave"]

    entities = [
        ModbusGenericSensor(coordinator=coordinator, slave=slave, **sensor)
        for sensor in SENSORS
    ]

    # Dodaj sensor diagnostyczny
    entities.append(ModbusUpdateIntervalSensor(coordinator=coordinator, slave=slave))

    # Metryki obliczane
    power_entity = entry.options.get("sensor_power")  # W lub kW
    if not power_entity:
        _LOGGER.warning("Nie skonfigurowano 'sensor_power' w opcjach integracji – COP będzie 'unavailable'.")

    entities.extend([
        RekuEfficiencySensor(coordinator=coordinator, slave=slave),
        RekuRecoveryPowerSensor(coordinator=coordinator, slave=slave),
        RekuCOPSensor(coordinator=coordinator, slave=slave, power_entity=power_entity),
    ])

    async_add_entities(entities)

class ModbusGenericSensor(SensorEntity):
    """Representation of a standard Modbus sensor."""

    def __init__(self, coordinator: ThesslaGreenCoordinator, name, address, input_type="holding", scale=1.0, precision=0, unit=None, icon=None, slave=1):
        self.coordinator = coordinator
        self._address = address
        self._input_type = input_type
        self._scale = scale
        self._precision = precision
        self._unit = unit
        self._slave = slave
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_native_value = None
        self._attr_icon = icon
        self._attr_unique_id = f"thessla_sensor_{slave}_{address}"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{slave}")},
            "name": "Rekuperator Thessla",
            "manufacturer": "Thessla Green",
            "model": "Modbus Rekuperator",
        }

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def native_value(self):
        if self._input_type == "input":
            raw_value = self.coordinator.safe_data.input.get(self._address)
        else:
            raw_value = self.coordinator.safe_data.holding.get(self._address)

        if raw_value is None:
            return None

        # Konwersja na signed int16
        raw = raw_value
        if raw > 0x7FFF:
            raw -= 0x10000

        value = raw * self._scale
        return round(value, self._precision)

    async def async_update(self):
        # Brak potrzeby ręcznego update — coordinator steruje
        pass

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

class ModbusUpdateIntervalSensor(SensorEntity):
    """Diagnostic sensor showing time between full Modbus updates."""

    def __init__(self, coordinator: ThesslaGreenCoordinator, slave: int):
        self.coordinator = coordinator
        self._slave = slave
        self._attr_name = "Modbus Update Interval"
        self._attr_native_unit_of_measurement = UnitOfTime.SECONDS
        self._attr_unique_id = f"thessla_update_interval_{slave}"
        self._attr_icon = "mdi:clock-time-eight"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{slave}")},
            "name": "Rekuperator Thessla",
            "manufacturer": "Thessla Green",
            "model": "Modbus Rekuperator",
        }

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def native_value(self):
        return self.coordinator.safe_data.update_interval

    async def async_update(self):
        # Niepotrzebne — wszystko przez coordinator
        pass

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

# =============================
#  Metryki: sprawność / moc / COP
# =============================

class _BaseComputedSensor(SensorEntity):
    """Baza dla sensorów liczonych z koordynatora."""
    _attr_should_poll = False

    def __init__(self, coordinator: ThesslaGreenCoordinator, slave: int):
        self.coordinator = coordinator
        self._slave = slave
        self._attr_native_value = None
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{slave}")},
            "name": "Rekuperator Thessla",
            "manufacturer": "Thessla Green",
            "model": "Modbus Rekuperator",
        }

    @property
    def available(self):
        return self.coordinator.last_update_success and self._attr_native_value is not None

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self._handle_coordinator_update))
        self._recalc()
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self):
        self._recalc()
        self.async_write_ha_state()

    # Helpers (adresy „na sztywno” wg Twoich definicji):
    def _read_temp_czerpnia(self) -> float | None:
        return self._read_input_scaled(addr=16, scale=0.1, precision=1)

    def _read_temp_nawiew(self) -> float | None:
        return self._read_input_scaled(addr=17, scale=0.1, precision=1)

    def _read_temp_wywiew(self) -> float | None:
        return self._read_input_scaled(addr=18, scale=0.1, precision=1)

    def _read_flow_nawiew(self) -> float | None:
        return self._read_holding_scaled(addr=256, scale=1.0)

    def _read_input_scaled(self, addr: int, scale: float, precision: int) -> float | None:
        raw = self.coordinator.safe_data.input.get(addr)
        if raw is None:
            return None
        if raw > 0x7FFF:
            raw -= 0x10000
        return round(raw * scale, precision)

    def _read_holding_scaled(self, addr: int, scale: float) -> float | None:
        raw = self.coordinator.safe_data.holding.get(addr)
        if raw is None:
            return None
        if raw > 0x7FFF:
            raw -= 0x10000
        return float(raw) * scale

    def _recalc(self):
        raise NotImplementedError


class RekuEfficiencySensor(_BaseComputedSensor):
    """Sprawność [%] = ((Tnawiew - Tczerpnia) / (Twywiew - Tczerpnia)) * 100"""
    def __init__(self, coordinator: ThesslaGreenCoordinator, slave: int):
        super().__init__(coordinator, slave)
        self._attr_name = "Rekuperator – sprawność"
        self._attr_unique_id = f"thessla_efficiency_{slave}"
        self._attr_icon = "mdi:percent"
        self._attr_native_unit_of_measurement = "%"

    def _recalc(self):
        To = self._read_temp_czerpnia()
        Te = self._read_temp_wywiew()
        Ts = self._read_temp_nawiew()
        if None in (To, Te, Ts):
            self._attr_native_value = None
            return
        denom = Te - To
        if abs(denom) < 0.5:
            self._attr_native_value = None
            return
        self._attr_native_value = round(((Ts - To) / denom) * 100.0, 1)


class RekuRecoveryPowerSensor(_BaseComputedSensor):
    """Moc odzysku [kW] ≈ 0.000335 * V[m3/h] * ΔT[°C]"""
    def __init__(self, coordinator: ThesslaGreenCoordinator, slave: int):
        super().__init__(coordinator, slave)
        self._attr_name = "Rekuperator – moc odzysku"
        self._attr_unique_id = f"thessla_recovery_power_{slave}"
        self._attr_icon = "mdi:fire"
        self._attr_native_unit_of_measurement = "kW"

    def _recalc(self):
        To = self._read_temp_czerpnia()
        Ts = self._read_temp_nawiew()
        flow = self._read_flow_nawiew()  # m3/h
        if None in (To, Ts) or flow is None or flow <= 0:
            self._attr_native_value = None
            return
        q_kw = 0.000335 * flow * (Ts - To)
        self._attr_native_value = round(q_kw, 3)


class RekuCOPSensor(_BaseComputedSensor):
    """COP = (moc odzysku [kW]) / (pobór elektryczny [kW]) – bez jednostki"""
    @property
    def native_unit_of_measurement(self):
        return None  # ratio

    def __init__(self, coordinator: ThesslaGreenCoordinator, slave: int, power_entity: str | None):
        super().__init__(coordinator, slave)
        self._attr_name = "Rekuperator – COP odzysku"
        self._attr_unique_id = f"thessla_cop_{slave}"
        self._attr_icon = "mdi:chart-line"
        self._power_entity = power_entity
        self._last_power_val = None
        self._last_power_unit = None

    @property
    def extra_state_attributes(self):
        return {
            "power_entity": self._power_entity,
            "power_value_raw": self._last_power_val,
            "power_unit": self._last_power_unit,
        }

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        # nasłuch zmian sensora mocy
        if self._power_entity:
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass,
                    [self._power_entity],
                    lambda ev: (self._recalc(), self.async_write_ha_state()),
                )
            )

    def _read_power_kw(self) -> float | None:
        """Czyta sensor mocy z HA, zwraca w kW (auto-konwersja W→kW)."""
        if not self._power_entity:
            return None
        st = self.hass.states.get(self._power_entity)
        if not st:
            return None

        unit = (st.attributes.get("unit_of_measurement") or "").strip()
        self._last_power_unit = unit

        try:
            val = float(st.state)
        except (TypeError, ValueError):
            self._last_power_val = st.state
            return None

        self._last_power_val = val
        u = unit.lower()

        if u in ("w", "watt"):
            return val / 1000.0
        if u == "kw":
            return val
        if "kwh" in u:
            _LOGGER.warning(
                "Wybrany sensor '%s' podaje energię (%s), a nie moc. COP wymaga mocy chwilowej w W/kW.",
                self._power_entity, unit
            )
            return None
        # Brak/inna jednostka — traktuj jako kW (log diagnostyczny)
        _LOGGER.debug("Sensor mocy '%s' ma jednostkę '%s' – przyjmuję jako kW.", self._power_entity, unit)
        return val

    def _recalc(self):
        To = self._read_temp_czerpnia()
        Ts = self._read_temp_nawiew()
        flow = self._read_flow_nawiew()
        p_kw = self._read_power_kw()

        if None in (To, Ts) or flow is None or flow <= 0 or p_kw is None or p_kw <= 0:
            self._attr_native_value = None
            return

        q_kw = 0.000335 * flow * (Ts - To)
        self._attr_native_value = round(q_kw / p_kw, 2) if q_kw > 0 else None