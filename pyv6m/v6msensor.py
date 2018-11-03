"""
Support for V6M sensors.

Michael Dubno - 2018 - New York
"""
import logging
import voluptuous as vol
from homeassistant.components.binary_sensor import (
    BinarySensorDevice, PLATFORM_SCHEMA)
from homeassistant.components.homeworks import (
    HomeworksDevice)
from homeassistant.const import CONF_SENSORS
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['v6m']
REQUIREMENTS = ['pyv6m==0.0.1']

CONF_CONTROLLER = 'controller'
CONF_ADDR = 'addr'

SENSOR_SCHEMA = vol.Schema({cv.positive_int: cv.string})
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_CONTROLLER, default = 'V6M'): cv.string,
    vol.Required(CONF_SENSORS): vol.All(cv.ensure_list, [SENSOR_SCHEMA])
})


def setup_platform(hass, config, add_entities, discover_info=None):
    """Set up the V6M sensors."""
    controller_name = config.get(CONF_CONTROLLER)
    controller = hass.data[controller_name]
    devs = []
    for sensor in config.get(CONF_SENSORS):
        # FIX: This should be done differently
        for num, title in sensor.items():
            dev.append(V6MSensor(controller, num, name))
    add_entities(devs, True)
    return True


class V6MSensor(V6MDevice, BinarySensorDevice):
    """V6M Sensor."""

    def __init__(self, controller, num, name):
        """Create sensor with addr and name."""
        HomeworksDevice.__init__(self, controller, num, name)
        self._num = num
        self._state = None

    @property
    def is_on(self):
        """Return state of the sensor."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return supported attributes."""
        return {"Sensor Number": self._num}

    def callback(self, num, old_state, new_state):
        """Callback to process state change."""
        self._state = new_state
        return True
