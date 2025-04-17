from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN

# Definicja tylko jednego sensora
SENSOR_DEFS = [
    ("Temperatura Czerpnia", 16, "input", UnitOfTemperature.CELSIUS, 0.1, 1),
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Konfiguracja sensorów dla wpisu w UI."""
    handler = hass.data[DOMAIN]["handler"]
    
    # Tworzenie sensorów na podstawie definicji (tylko jeden sensor)
    sensors = [
        ThesslaGreenSensor(name, address, input_type, unit, scale, precision, handler)
        for name, address, input_type, unit, scale, precision in SENSOR_DEFS
    ]
    
    # Dodanie sensorów do Home Assistant
    async_add_entities(sensors)

class ThesslaGreenSensor(SensorEntity):
    """Reprezentacja sensora do odczytu wartości z Modbusa."""
    def __init__(self, name, address, input_type, unit, scale, precision, handler):
        self._attr_name = f"Rekuperator {name}"
        self._attr_unique_id = f"thessla_sensor_{address}"
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = "measurement"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "thessla_green_device")},
            name="Thessla Green",
            manufacturer="Thessla",
            model="Thessla Green Rekuperator",
        )
        self._handler = handler
        self._address = address
        self._input_type = input_type
        self._scale = scale
        self._precision = precision
        self._value = None

    @property
    def native_value(self):
        """Zwraca wartość sensora."""
        return self._value

    async def async_update(self):
        """Aktualizacja wartości sensora z rejestru Modbusa."""
        result = await self._handler.read_register(self._address, input_type=self._input_type)
        if result:
            val = result[0] * self._scale
            if self._precision is not None:
                val = round(val, self._precision)
            self._value = val