"""Platform for switch integration."""

import voluptuous as vol

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers import entity_platform

from .const import ATTR_DEVICE_LIST, DOMAIN, LAMBDA_UPDATE_SHADOW
from .device import MoenFaucetDevice
from .entity import MoenEntity

SERVICE_SEND_PAYLOAD = "send_payload"


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add sensors for passed config_entry in HA."""
    devices: MoenFaucetDevice = hass.data[DOMAIN][config_entry.entry_id][
        ATTR_DEVICE_LIST
    ]

    new_devices = []
    for device in devices:
        new_devices.append(FaucetSwitch(device))
    if new_devices:
        async_add_devices(new_devices)
        _async_setup_services()


def _async_setup_services():
    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        SERVICE_SEND_PAYLOAD,
        {
            vol.Required("payload"): dict,
        },
        "async_send_payload",
    )


class FaucetSwitch(MoenEntity, SwitchEntity):
    """Representation of a Battery Sensor."""

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return f"{super().unique_id}_switch"

    @property
    def is_on(self):
        """Return is the switch on."""
        return self._device.state == "running"

    @property
    def name(self):
        """Return the name of the switch."""
        return f"{self._device.name} Switch"

    async def async_send_payload(self, payload: dict):
        """Send a playload to the faucet."""
        await self.hass.async_add_executor_job(
            self._device.send_payload,
            LAMBDA_UPDATE_SHADOW,
            payload,
        )

    async def async_turn_on(self, **kwargs):
        """Turn the fuacet on."""
        await self.hass.async_add_executor_job(
            self._device.send_payload,
            LAMBDA_UPDATE_SHADOW,
            {"command": "run", "commandSrc": "app"},
        )
        self._device.set_state("running")
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the fuacet off."""
        await self.hass.async_add_executor_job(
            self._device.send_payload,
            LAMBDA_UPDATE_SHADOW,
            {"command": "stop", "commandSrc": "app"},
        )
        self._device.set_state("idle")
        self.async_write_ha_state()
