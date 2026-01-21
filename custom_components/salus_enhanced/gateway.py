"""Gateway factory and wrapper classes for Salus devices."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

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


class IT600Gateway(SalusGatewayBase):
    """Wrapper for IT600 local gateway."""

    def __init__(self, host: str, euid: str):
        """Initialize IT600 gateway."""
        from pyit600.gateway import IT600Gateway as PyIT600Gateway
        
        self._gateway = PyIT600Gateway(host=host, euid=euid)

    async def connect(self) -> None:
        """Connect to the gateway."""
        await self._gateway.connect()

    async def poll_status(self) -> dict[str, Any]:
        """Poll status from gateway."""
        await self._gateway.poll_status()
        return {
            "climate": self._gateway.get_climate_devices(),
            "binary_sensor": self._gateway.get_binary_sensor_devices(),
            "sensor": self._gateway.get_sensor_devices(),
            "switch": self._gateway.get_switch_devices(),
            "cover": self._gateway.get_cover_devices(),
        }

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

    async def set_climate_device_temperature(self, device_id: str, temperature: float) -> None:
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


class IT500Gateway(SalusGatewayBase):
    """Wrapper for IT500 cloud gateway."""

    def __init__(self, username: str, password: str, device_id: str):
        """Initialize IT500 gateway."""
        self._username = username
        self._password = password
        self._device_id = device_id
        self._client = None
        self._device_data = {}

    async def connect(self) -> None:
        """Connect to the gateway."""
        try:
            from pyit500.client import IT500Client
            
            self._client = IT500Client(self._username, self._password)
            await self._client.login()
        except ImportError:
            _LOGGER.error(
                "pyit500 library not available. Install with: pip install pyit500"
            )
            raise

    async def poll_status(self) -> dict[str, Any]:
        """Poll status from gateway."""
        if not self._client:
            raise RuntimeError("Gateway not connected")

        device_data = await self._client.get_device_data(self._device_id)
        
        # Transform IT500 data to common format
        self._device_data = {
            "climate": {
                self._device_id: {
                    "model": device_data.get("product", "IT500"),
                    "current_temperature": device_data.get("CH1currentTemperature"),
                    "target_temperature": device_data.get("CH1currentSetPoint"),
                    "hvac_mode": self._get_hvac_mode(device_data),
                    "is_heating": device_data.get("CH1heatOnOff") == 1,
                    "preset_mode": device_data.get("CH1autoOff", "manual"),
                }
            },
            "binary_sensor": {},
            "sensor": {},
            "switch": {},
            "cover": {},
        }
        
        return self._device_data

    def _get_hvac_mode(self, data: dict) -> str:
        """Get HVAC mode from IT500 data."""
        if data.get("CH1heatOffOn") == 0:
            return "off"
        if data.get("CH1autoOff") == "auto":
            return "auto"
        return "heat"

    async def close(self) -> None:
        """Close connection to gateway."""
        if self._client:
            await self._client.close()

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

    async def set_climate_device_temperature(self, device_id: str, temperature: float) -> None:
        """Set climate device temperature."""
        if not self._client:
            raise RuntimeError("Gateway not connected")
        await self._client.set_temperature(device_id, temperature)

    async def set_climate_device_mode(self, device_id: str, mode: str) -> None:
        """Set climate device mode."""
        if not self._client:
            raise RuntimeError("Gateway not connected")
        
        mode_map = {"heat": 1, "off": 0, "auto": 1}
        await self._client.set_mode(device_id, mode_map.get(mode, 1))

    async def set_climate_device_preset(self, device_id: str, preset: str) -> None:
        """Set climate device preset."""
        if not self._client:
            raise RuntimeError("Gateway not connected")
        await self._client.set_preset(device_id, preset)


def create_gateway(gateway_type: str, **kwargs) -> SalusGatewayBase:
    """Create appropriate gateway based on type."""
    if gateway_type == GATEWAY_TYPE_IT600:
        return IT600Gateway(
            host=kwargs["host"],
            euid=kwargs["euid"],
        )
    elif gateway_type == GATEWAY_TYPE_IT500:
        return IT500Gateway(
            username=kwargs["username"],
            password=kwargs["password"],
            device_id=kwargs["device_id"],
        )
    else:
        raise ValueError(f"Unknown gateway type: {gateway_type}")
