"""Gateway factory and wrapper classes for Salus devices."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

from .const import GATEWAY_TYPE_IT500, GATEWAY_TYPE_IT600

_LOGGER = logging.getLogger(__name__)


class SalusGatewayBase(ABC):
    """Base class for Salus gateways."""

    @abstractmethod
    async def connect(self) -> None:
        """Connect to the gateway."""

    @abstractmethod
    async def poll_status(self) -> dict[str, Any]:
        """Poll status from gateway."""

    @abstractmethod
    async def close(self) -> None:
        """Close connection to gateway."""

    @abstractmethod
    def get_climate_devices(self) -> dict[str, Any]:
        """Get climate devices."""

    @abstractmethod
    def get_binary_sensor_devices(self) -> dict[str, Any]:
        """Get binary sensor devices."""

    @abstractmethod
    def get_sensor_devices(self) -> dict[str, Any]:
        """Get sensor devices."""

    @abstractmethod
    def get_switch_devices(self) -> dict[str, Any]:
        """Get switch devices."""

    @abstractmethod
    def get_cover_devices(self) -> dict[str, Any]:
        """Get cover devices."""


# ---------------------------------------------------------------------------
# IT600 (local) – bazat pe pyit600
# ---------------------------------------------------------------------------


class IT600Gateway(SalusGatewayBase):
    """Wrapper for IT600 local gateway."""

    def __init__(self, host: str, euid: str) -> None:
        """Initialize IT600 gateway."""
        # Lazy import – doar când chiar folosim IT600
        from pyit600.gateway import IT600Gateway as PyIT600Gateway

        self._gateway = PyIT600Gateway(host=host, euid=euid)

    async def connect(self) -> None:
        """Connect to the gateway."""
        await self._gateway.connect()

    async def poll_status(self) -> dict[str, Any]:
        """Poll status from gateway."""
        await self._gateway.poll_status()
        data = {
            "climate": self._gateway.get_climate_devices(),
            "binary_sensor": self._gateway.get_binary_sensor_devices(),
            "sensor": self._gateway.get_sensor_devices(),
            "switch": self._gateway.get_switch_devices(),
            "cover": self._gateway.get_cover_devices(),
        }
        return data

    async def close(self) -> None:
        """Close connection to gateway."""
        await self._gateway.close()

    def get_climate_devices(self) -> dict[str, Any]:
        """Get climate devices."""
        return self._gateway.get_climate_devices()

    def get_binary_sensor_devices(self) -> dict[str, Any]:
        """Get binary sensor devices."""
        return self._gateway.get_binary_sensor_devices()

    def get_sensor_devices(self) -> dict[str, Any]:
        """Get sensor devices."""
        return self._gateway.get_sensor_devices()

    def get_switch_devices(self) -> dict[str, Any]:
        """Get switch devices."""
        return self._gateway.get_switch_devices()

    def get_cover_devices(self) -> dict[str, Any]:
        """Get cover devices."""
        return self._gateway.get_cover_devices()

    async def set_climate_device_temperature(
        self, device_id: str, temperature: float
    ) -> None:
        """Set climate device temperature."""
        await self._gateway.set_climate_device_temperature(device_id, temperature)

    async def set_climate_device_mode(self, device_id: str, mode: str) -> None:
        """Set climate device mode."""
        await self._gateway.set_climate_device_mode(device_id, mode)

    async def set_climate_device_preset(self, device_id: str, preset: str) -> None:
        """Set climate device preset."""
        await self._gateway.set_climate_device_preset(device_id, preset)

    async def turn_on_switch_device(self, device_id: str) -> None:
        """Turn on switch device."""
        await self._gateway.turn_on_switch_device(device_id)

    async def turn_off_switch_device(self, device_id: str) -> None:
        """Turn off switch device."""
        await self._gateway.turn_off_switch_device(device_id)

    async def open_cover_device(self, device_id: str) -> None:
        """Open cover device."""
        await self._gateway.open_cover_device(device_id)

    async def close_cover_device(self, device_id: str) -> None:
        """Close cover device."""
        await self._gateway.close_cover_device(device_id)

    async def stop_cover_device(self, device_id: str) -> None:
        """Stop cover device."""
        await self._gateway.stop_cover_device(device_id)

    async def set_cover_position(self, device_id: str, position: int) -> None:
        """Set cover position."""
        await self._gateway.set_cover_position(device_id, position)


# ---------------------------------------------------------------------------
# IT500 (cloud) – bazat pe pyit500
# ---------------------------------------------------------------------------


class IT500Gateway(SalusGatewayBase):
    """Wrapper for IT500 cloud gateway."""

    def __init__(self, username: str, password: str, device_id: str) -> None:
        """Initialize IT500 gateway."""
        self._username = username
        self._password = password
        self._device_id = device_id
        self._client = None
        self._device_data: Dict[str, Any] = {}

    async def connect(self) -> None:
        """Initialize client and verify credentials.

        NOTE: pyit500 does not expose a login() method on PyIt500.
        Auth.async_login() is responsible for authenticating.
        """
        try:
            from pyit500.pyit500 import PyIt500
            from pyit500.auth import Auth
        except Exception as err:
            _LOGGER.error("pyit500 library not available: %s", err)
            raise

        # Auth handles login internally via async_login
        auth = await Auth.async_login(self._username, self._password)
        self._client = PyIt500(auth)

        # Optional sanity check – fetch user
        try:
            await self._client.async_get_user()
        except Exception as err:
            _LOGGER.error("Failed to fetch IT500 user: %s", err)
            raise

    async def poll_status(self) -> dict[str, Any]:
        """Poll status from IT500 cloud."""
        if not self._client:
            raise RuntimeError("IT500 gateway not connected")

        # Fetch device object from API
        device = await self._client.async_get_device(self._device_id)

        # Try to convert Device object to a dict-like structure
        if isinstance(device, dict):
            raw = device
        elif hasattr(device, "to_dict"):
            raw = device.to_dict()
        elif hasattr(device, "__dict__"):
            raw = vars(device)
        else:
            raw = {}
            _LOGGER.warning(
                "Unsupported device type returned from pyit500 for %s: %s",
                self._device_id,
                type(device),
            )

        # Map to common structure, using IT500-style field names if present
        model = raw.get("product", "IT500")

        current_temp = raw.get("CH1currentTemperature")
        target_temp = raw.get("CH1currentSetPoint")
        heat_on_off = raw.get("CH1heatOnOff")
        heat_off_on = raw.get("CH1heatOffOn")
        auto_off = raw.get("CH1autoOff", "manual")

        hvac_mode = self._get_hvac_mode(heat_off_on, auto_off)
        is_heating = heat_on_off == 1

        self._device_data = {
            "climate": {
                self._device_id: {
                    "model": model,
                    "current_temperature": current_temp,
                    "target_temperature": target_temp,
                    "hvac_mode": hvac_mode,
                    "is_heating": is_heating,
                    "preset_mode": auto_off,
                }
            },
            "binary_sensor": {},
            "sensor": {},
            "switch": {},
            "cover": {},
        }

        return self._device_data

    @staticmethod
    def _get_hvac_mode(heat_off_on: Any, auto_off: Any) -> str:
        """Get HVAC mode from IT500 flags."""
        if heat_off_on == 0:
            return "off"
        if auto_off == "auto":
            return "auto"
        return "heat"

    async def close(self) -> None:
        """Close connection.

        pyit500 does not expose an explicit close(), so this is a no-op.
        """
        # Nothing to close for HTTP-based API, but method kept for interface compatibility.
        return

    def get_climate_devices(self) -> dict[str, Any]:
        """Get climate devices."""
        return self._device_data.get("climate", {})

    def get_binary_sensor_devices(self) -> dict[str, Any]:
        """Get binary sensor devices."""
        return self._device_data.get("binary_sensor", {})

    def get_sensor_devices(self) -> dict[str, Any]:
        """Get sensor devices."""
        return self._device_data.get("sensor", {})

    def get_switch_devices(self) -> dict[str, Any]:
        """Get switch devices."""
        return self._device_data.get("switch", {})

    def get_cover_devices(self) -> dict[str, Any]:
        """Get cover devices."""
        return self._device_data.get("cover", {})

    # Pentru moment, facem IT500 doar read-only; scrierea depinde
    # de ce metode oferă librăria Device/pyit500 (nu sunt în snippetul pe care îl avem).

    async def set_climate_device_temperature(
        self, device_id: str, temperature: float
    ) -> None:
        """Set climate device temperature (NOT IMPLEMENTED YET)."""
        raise NotImplementedError("Setting temperature is not implemented for IT500 yet")

    async def set_climate_device_mode(self, device_id: str, mode: str) -> None:
        """Set climate device mode (NOT IMPLEMENTED YET)."""
        raise NotImplementedError("Setting mode is not implemented for IT500 yet")

    async def set_climate_device_preset(self, device_id: str, preset: str) -> None:
        """Set climate device preset (NOT IMPLEMENTED YET)."""
        raise NotImplementedError("Setting preset is not implemented for IT500 yet")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def create_gateway(gateway_type: str, **kwargs) -> SalusGatewayBase:
    """Create appropriate gateway based on type."""
    if gateway_type == GATEWAY_TYPE_IT600:
        return IT600Gateway(
            host=kwargs["host"],
            euid=kwargs["euid"],
        )

    if gateway_type == GATEWAY_TYPE_IT500:
        return IT500Gateway(
            username=kwargs["username"],
            password=kwargs["password"],
            device_id=kwargs["device_id"],
        )

    raise ValueError(f"Unknown gateway type: {gateway_type}")
