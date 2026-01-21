"""Config flow for Salus Enhanced integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_DEVICE_ID,
    CONF_EUID,
    CONF_GATEWAY_TYPE,
    DOMAIN,
    GATEWAY_TYPE_IT500,
    GATEWAY_TYPE_IT600,
)

_LOGGER = logging.getLogger(__name__)

STEP_GATEWAY_TYPE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_GATEWAY_TYPE): vol.In(
            {
                GATEWAY_TYPE_IT600: "IT600 (Local Gateway - UGE600)",
                GATEWAY_TYPE_IT500: "IT500 (Cloud - salus-it500.com)",
            }
        ),
    }
)

STEP_IT600_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_EUID, default="0000000000000000"): str,
    }
)

STEP_IT500_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_DEVICE_ID): str,
    }
)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

class InvalidAuth(HomeAssistantError):
    """Error to indicate invalid authentication."""


class InvalidDeviceId(HomeAssistantError):
    """Error to indicate invalid or malformed device id."""
    

async def validate_it600(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate IT600 gateway connection."""
    # importăm gateway lazy, ca să nu stricăm importul config_flow dacă lipsesc librăriile
    try:
        from .gateway import create_gateway
    except Exception as err:  # ModuleNotFoundError, ImportError etc.
        _LOGGER.error("Failed to import gateway module for IT600: %s", err)
        raise CannotConnect from err

    gateway = create_gateway(
        GATEWAY_TYPE_IT600,
        host=data[CONF_HOST],
        euid=data[CONF_EUID],
    )

    try:
        await gateway.connect()
        await gateway.poll_status()
        await gateway.close()
    except Exception as err:
        _LOGGER.error("Failed to connect to IT600 gateway: %s", err)
        raise CannotConnect from err

    return {"title": f"Salus IT600 Gateway {data[CONF_EUID]}"}


async def validate_it500(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Basic validation for IT500 cloud config.

    We do NOT talk to pyit500 here to avoid import/runtime issues during config flow.
    Real connectivity errors are handled in async_setup_entry.
    """
    username = data.get(CONF_USERNAME, "").strip()
    password = data.get(CONF_PASSWORD, "")
    device_id = data.get(CONF_DEVICE_ID, "").strip()

    if not username or not password:
        raise InvalidAuth

    if not device_id.isdigit():
        raise InvalidDeviceId

    return {"title": f"Salus IT500 Device {device_id}"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Salus Enhanced Integration."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        self._gateway_type: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - select gateway type."""
        if user_input is not None:
            self._gateway_type = user_input[CONF_GATEWAY_TYPE]

            if self._gateway_type == GATEWAY_TYPE_IT600:
                return await self.async_step_it600()
            if self._gateway_type == GATEWAY_TYPE_IT500:
                return await self.async_step_it500()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_GATEWAY_TYPE_SCHEMA,
        )

    async def async_step_it600(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle IT600 gateway configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_it600(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected exception during IT600 validation")
                errors["base"] = "unknown"
            else:
                user_input[CONF_GATEWAY_TYPE] = GATEWAY_TYPE_IT600
                await self.async_set_unique_id(f"it600_{user_input[CONF_EUID]}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="it600",
            data_schema=STEP_IT600_SCHEMA,
            errors=errors,
            description_placeholders={
                "info": "Enter your IT600 local gateway details. Find EUID on the bottom of your gateway."
            },
        )

    async def async_step_it500(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle IT500 cloud configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_it500(self.hass, user_input)
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except InvalidDeviceId:
                errors["device_id"] = "invalid_device_id"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected exception during IT500 validation")
                errors["base"] = "unknown"
            else:
                user_input[CONF_GATEWAY_TYPE] = GATEWAY_TYPE_IT500
                await self.async_set_unique_id(f"it500_{user_input[CONF_DEVICE_ID]}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="it500",
            data_schema=STEP_IT500_SCHEMA,
            errors=errors,
            description_placeholders={
                "info": "Login to https://salus-it500.com and find Device ID in the URL (devId parameter)."
            },
        )
