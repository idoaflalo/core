"""Platform for sensor integration."""

from homeassistant.const import DEVICE_CLASS_BATTERY, PERCENTAGE

from .const import ATTR_DEVICE_LIST, DOMAIN
from .device import MoenFaucetDevice
from .entity import MoenEntity


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add sensors for passed config_entry in HA."""
    devices: MoenFaucetDevice = hass.data[DOMAIN][config_entry.entry_id][
        ATTR_DEVICE_LIST
    ]

    new_devices = []
    for device in devices:
        new_devices.append(FaucetBatterySensor(device))
    if new_devices:
        async_add_devices(new_devices)


class FaucetBatterySensor(MoenEntity):
    """Representation of a Battery Sensor."""

    device_class = DEVICE_CLASS_BATTERY

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return f"{super().unique_id}_battery"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._device.battery_percentage

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return PERCENTAGE

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._device.name} Battery"
