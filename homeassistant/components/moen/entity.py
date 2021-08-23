"""Base entity for Moen integration."""
from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .device import MoenFaucetDevice


class MoenEntity(Entity):
    """A base class for Moen entities."""

    _attr_should_poll = False

    def __init__(self, device: MoenFaucetDevice):
        """Init moen entity."""
        super().__init__()
        self._device: MoenFaucetDevice = device

    async def async_added_to_hass(self):
        """Register callback when entity about to be added to hass."""
        self._device.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Remove callback when entity will be removed from hass."""
        self._device.remove_callback(self.async_write_ha_state)

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return f"{DOMAIN}_{self._device.client_id}"

    @property
    def available(self) -> bool:
        """Return entity is available."""
        return self._device.connected

    @property
    def device_state_attributes(self):
        """Return the device attributes."""
        return self._device.attributes

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, super().unique_id)},
            "name": self._device.name,
            "manufacturer": DOMAIN.capitalize(),
            "model": self._device.sku,
            "sw_version": self._device.firmware_version,
        }
