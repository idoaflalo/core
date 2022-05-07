"""Device for Moen integration."""
import json
from typing import Callable, Set

from homeassistant.core import HomeAssistant, callback

from .api import MoenApi
from .const import MQTT_UPDATE_ACCEPTED_TOPIC


class MoenFaucetDevice:
    """Faucet device for moen integration."""

    def __init__(self, hass: HomeAssistant, api: MoenApi, device_meta: dict):
        """Init faucet device."""
        super().__init__()
        self._hass: HomeAssistant = hass
        self._api: MoenApi = api
        self._device_meta: dict = device_meta
        self._callbacks: Set[Callable] = set()
        self._loop = hass.loop
        self._initialize()

    def _initialize(self) -> None:
        self._api.subscribe_to_topic(
            MQTT_UPDATE_ACCEPTED_TOPIC.format(self.client_id),
            self._on_update,
        )

    @callback
    def _on_update(self, topic: str, payload: str, **kwargs) -> None:
        state = json.loads(payload)["state"]
        if "reported" in state:
            self._device_meta.update(state["reported"])
            for call in self._callbacks:
                self._loop.call_soon_threadsafe(call)

    def send_payload(self, function_name: str, payload: dict) -> None:
        """Send payload to the faucet for a given payload."""
        self._api.invoke_lambda_function(
            function_name, {"clientId": self.client_id, "payload": payload}
        )

    def register_callback(self, callback: Callable) -> None:
        """Register a callback for listening to updates."""
        self._callbacks.add(callback)

    def remove_callback(self, callback: Callable) -> None:
        """Remove a registered callback."""
        self._callbacks.discard(callback)

    def set_state(self, state: str) -> None:
        """Set faucet to the given state."""
        self._device_meta["state"] = state

    @property
    def extra_state_attributes(self) -> dict:
        """Return the device attributes."""
        return self._device_meta

    @property
    def name(self) -> str:
        """Return the device name."""
        return self._device_meta["nickname"]

    @property
    def client_id(self) -> str:
        """Return the device serial number."""
        return self._device_meta["clientId"]

    @property
    def sku(self) -> str:
        """Return the device SKU."""
        return self._device_meta["sku"]

    @property
    def connected(self) -> bool:
        """Return if the device is connected."""
        return self._device_meta["connected"]

    @property
    def state(self) -> str:
        """Return the state of the Device."""
        return self._device_meta["state"]

    @property
    def temperature(self) -> str:
        """Return the temparture of the water as celsius."""
        return self._device_meta["temperature"]

    @property
    def firmware_version(self) -> str:
        """Return the firmware version of the device."""
        return self._device_meta["firmwareVersion"]

    @property
    def battery_percentage(self) -> int:
        """Battery level as a percentage."""
        return self._device_meta["batteryPercentage"]
