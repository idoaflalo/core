"""The Moen integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import MoenApi
from .const import (
    ATTR_API,
    ATTR_DEVICE_LIST,
    DOMAIN,
    LAMBDA_GET_DEVICES,
    PASSWORD_FIELD,
    USERNAME_FIELD,
)
from .device import MoenFaucetDevice

PLATFORMS = ["switch", "sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Moen from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    moen_api = MoenApi(entry.data[USERNAME_FIELD], entry.data[PASSWORD_FIELD])

    await hass.async_add_executor_job(moen_api.connect)

    devices = await hass.async_add_executor_job(get_devices, hass, moen_api)

    hass.data[DOMAIN][entry.entry_id] = {ATTR_API: moen_api, ATTR_DEVICE_LIST: devices}

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    hass.data[DOMAIN][entry.entry_id][ATTR_API].disconnect()
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


def get_devices(hass: HomeAssistant, moen_api: MoenApi) -> list[MoenFaucetDevice]:
    """Get the devices from the moen API."""
    device_metas = moen_api.invoke_lambda_function(LAMBDA_GET_DEVICES)
    devices = []
    for device_meta in device_metas:
        devices.append(MoenFaucetDevice(hass, moen_api, device_meta))
    return devices
