"""Config flow for Moen integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .api import MoenApi
from .const import DOMAIN, PASSWORD_FIELD, TITLE_FIELD, USERNAME_FIELD

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(TITLE_FIELD): str,
        vol.Required(USERNAME_FIELD): str,
        vol.Required(PASSWORD_FIELD): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    api = MoenApi(data[USERNAME_FIELD], data[PASSWORD_FIELD])

    if len(data[TITLE_FIELD]) < 3:
        raise TitleTooShort

    try:
        await hass.async_add_executor_job(api.authenticate)
    except Exception:  # pylint: disable=broad-except
        raise InvalidAuth

    return {"title": data[TITLE_FIELD]}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Moen."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except TitleTooShort:
            errors["base"] = "title_too_short"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class TitleTooShort(HomeAssistantError):
    """Error to indicate title should contains at least 3 characters."""
