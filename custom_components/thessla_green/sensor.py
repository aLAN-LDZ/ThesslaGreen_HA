from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfTemperature, UnitOfVolume, PERCENTAGE
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN

# Definicje sensorów w jednym miejscu
SENSOR_DEFS = [
    ("Temperatura Czerpnia", 16, "input", UnitOfTemperature.CELSIUS, 0.1, 1),
    ("Temperatura Nawiew", 17, "input", UnitOfTemperature.CELSIUS, 0.1, 1),
    ("Temperatura Wywiew", 18, "input", UnitOfTemperature.CELSIUS, 0.1, 1),
    ("Temperatura za FPX", 19, "input", UnitOfTemperature.CELSIUS, 0.1, 1),
    ("Temperatura PCB", 22, "input", UnitOfTemperature.CELSIUS, 0.1, 1),
    ("Strumień nawiew", 256, "holding", UnitOfVolume.CUBIC_METERS_PER_HOUR, 1, 1),
    ("Strumień wywiew", 257, "holding", UnitOfVolume.CUBIC_METERS_PER_HOUR, 1, 1),
    ("speedmanual", 4210, "holding", PERCENTAGE, 1, 1),
    # dodajemy pozostałe jako surowe liczby
    ("tryb pracy", 4208, "holding", None, 1, 0),
    ("lato zima", 4209, "holding", None, 1, 0),
    ("Bypass", 4320, "holding", None, 1, 0),
    ("fpx flaga", 4192, "holding", None, 1, 0),
    ("FPX tryb", 4198, "holding", None, 1, 0),
    ("Alarm", 8192, "holding", None, 1, 0),
    ("Error", 8193, "holding", None, 1, 0),
    ("FPX zabezpieczenie termiczne", 8208, "holding", None, 1, 0),
    ("Awaria Wentylatora Nawiewu", 8222, "holding", None, 1, 0),
    ("Awaria Wentylatora Wywiewu", 8223, "holding", None, 1, 0),
    ("Awaria CF Nawiewu", 8330, "holding", None, 1, 0),
    ("Awaria CF Wywiewu", 8331, "holding", None, 1, 0),
    ("Wymiana Filtrów", 8444, "holding", None, 1, 0),
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Konfiguracja sensorów dla wpisu w UI."""
    handler = hass.data[DOMAIN]["handler"]
    
    # Tworzenie sensorów na podstawie definicji
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