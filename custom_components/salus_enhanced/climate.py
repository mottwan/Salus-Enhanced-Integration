"""Support for Salus climate devices."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_BATTERY, ATTR_HUMIDITY, ATTR_WINDOW_OPEN, DEVICE_MODELS, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Salus climate devices."""
    data = hass.data[DOMAIN][entry.entry_id]
    gateway = data["gateway"]
    coordinator = data["coordinator"]

    entities = []
    climate_devices = coordinator.data.get("climate", {})

    for device_id, device_data in climate_devices.items():
        entities.append(SalusClimate(coordinator, gateway, device_id, device_data))

    async_add_entities(entities)


class SalusClimate(CoordinatorEntity, ClimateEntity):
    """Representation of a Salus climate device."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.PRESET_MODE
    )
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF, HVACMode.AUTO]
    _attr_preset_modes = ["home", "away", "sleep", "manual"]

    def __init__(self, coordinator, gateway, device_id, device_data):
        """Initialize the climate device."""
        super().__init__(coordinator)
        self._gateway = gateway
        self._device_id = device_id
        self._attr_unique_id = f"{DOMAIN}_{device_id}_climate"
        
        # Get device model info
        model = device_data.get("model", "Unknown")
        gateway_type = coordinator.data.get("gateway_type", "it600")
        
        # Get model info from appropriate device models dict
        from .const import DEVICE_MODELS
        device_models = DEVICE_MODELS.get(gateway_type, {}).get("climate", {})
        model_info = device_models.get(model, {})
        
        self._attr_name = f"{model_info.get('name', 'Salus Thermostat')} {device_id}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "name": self._attr_name,
            "manufacturer": "Salus",
            "model": model,
        }

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        device_data = self.coordinator.data.get("climate", {}).get(self._device_id, {})
        return device_data.get("current_temperature")

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        device_data = self.coordinator.data.get("climate", {}).get(self._device_id, {})
        return device_data.get("target_temperature")

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        device_data = self.coordinator.data.get("climate", {}).get(self._device_id, {})
        mode = device_data.get("hvac_mode", "off")
        
        if mode == "heat":
            return HVACMode.HEAT
        elif mode == "auto":
            return HVACMode.AUTO
        return HVACMode.OFF

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return current HVAC action."""
        device_data = self.coordinator.data.get("climate", {}).get(self._device_id, {})
        if device_data.get("is_heating"):
            return HVACAction.HEATING
        if self.hvac_mode == HVACMode.OFF:
            return HVACAction.OFF
        return HVACAction.IDLE

    @property
    def preset_mode(self) -> str | None:
        """Return current preset mode."""
        device_data = self.coordinator.data.get("climate", {}).get(self._device_id, {})
        return device_data.get("preset_mode", "manual")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        device_data = self.coordinator.data.get("climate", {}).get(self._device_id, {})
        attributes = {}
        
        if battery := device_data.get("battery"):
            attributes[ATTR_BATTERY] = battery
        if humidity := device_data.get("humidity"):
            attributes[ATTR_HUMIDITY] = humidity
        if window_open := device_data.get("window_open"):
            attributes[ATTR_WINDOW_OPEN] = window_open
            
        return attributes

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return

        await self._gateway.set_climate_device_temperature(self._device_id, temperature)
        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""
        mode_mapping = {
            HVACMode.HEAT: "heat",
            HVACMode.AUTO: "auto",
            HVACMode.OFF: "off",
        }
        
        if hvac_mode in mode_mapping:
            await self._gateway.set_climate_device_mode(
                self._device_id, mode_mapping[hvac_mode]
            )
            await self.coordinator.async_request_refresh()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        await self._gateway.set_climate_device_preset(self._device_id, preset_mode)
        await self.coordinator.async_request_refresh()
