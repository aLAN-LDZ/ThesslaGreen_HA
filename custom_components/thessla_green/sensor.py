from homeassistant.helpers.entity import Entity

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    async_add_entities([ThesslaTemperatureSensor()])

class ThesslaTemperatureSensor(Entity):
    def __init__(self):
        self._state = 21.5

    @property
    def name(self):
        return "Thessla Temperature"

    @property
    def state(self):
        return self._state
