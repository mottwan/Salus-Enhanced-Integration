"""Constants for the Salus Enhanced integration."""
from homeassistant.const import Platform

DOMAIN = "salus_enhanced_integration"

# Configuration
CONF_EUID = "euid"
CONF_GATEWAY_TYPE = "gateway_type"
CONF_DEVICE_ID = "device_id"

# Gateway types
GATEWAY_TYPE_IT600 = "it600"
GATEWAY_TYPE_IT500 = "it500"

SCAN_INTERVAL = 30

SUPPORTED_PLATFORMS = [
    Platform.CLIMATE,
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.COVER,
]

# Device model mappings - IT600 models
IT600_DEVICE_MODELS = {
    "climate": {
        "HTRP-RF": {"name": "Salus HTRP-RF Thermostat"},
        "HTRP-RF50": {"name": "Salus HTRP-RF50 Thermostat"},
        "TS600": {"name": "Salus TS600 Thermostat"},
        "VS10WRF": {"name": "Salus VS10 White Thermostat"},
        "VS10BRF": {"name": "Salus VS10 Black Thermostat"},
        "VS20WRF": {"name": "Salus VS20 White Thermostat"},
        "VS20BRF": {"name": "Salus VS20 Black Thermostat"},
        "SQ610": {"name": "Salus SQ610 Thermostat"},
        "SQ610RF": {"name": "Salus SQ610RF Thermostat"},
        "FC600": {"name": "Salus FC600 Fan Coil Thermostat"},
    },
    "binary_sensor": {
        "SW600": {"name": "Salus SW600 Window Sensor"},
        "WLS600": {"name": "Salus WLS600 Water Leak Sensor"},
        "OS600": {"name": "Salus OS600 Occupancy Sensor"},
        "SD600": {"name": "Salus SD600 Smoke Detector"},
        "TRV10RFM": {"name": "Salus TRV10RFM Radiator Valve"},
        "RX10RF": {"name": "Salus RX10RF Receiver"},
        "MS600": {"name": "Salus MS600 Motion Sensor"},
    },
    "sensor": {
        "PS600": {"name": "Salus PS600 Temperature Sensor"},
    },
    "switch": {
        "SPE600": {"name": "Salus SPE600 Smart Plug"},
        "RS600": {"name": "Salus RS600 Relay Switch"},
        "SR600": {"name": "Salus SR600 Switching Receiver"},
        "SP600": {"name": "Salus SP600 Smart Plug"},
    },
    "cover": {
        "RS600": {"name": "Salus RS600 Shutter Controller"},
    },
}

# Device model mappings - IT500 models
IT500_DEVICE_MODELS = {
    "climate": {
        "IT500": {"name": "Salus IT500 Thermostat"},
        "RT310i": {"name": "Salus RT310i Thermostat"},
        "RT310": {"name": "Salus RT310 Thermostat"},
        "RT510": {"name": "Salus RT510 Thermostat"},
        "RT520": {"name": "Salus RT520 Thermostat"},
        "XT500": {"name": "Salus XT500 Thermostat"},
    },
}

# Combined device models
DEVICE_MODELS = {
    GATEWAY_TYPE_IT600: IT600_DEVICE_MODELS,
    GATEWAY_TYPE_IT500: IT500_DEVICE_MODELS,
}

# Attribute mappings for better entity support
ATTR_BATTERY = "battery"
ATTR_SIGNAL = "signal_strength"
ATTR_HUMIDITY = "humidity"
ATTR_VALVE_POSITION = "valve_position"
ATTR_WINDOW_OPEN = "window_open"
ATTR_HEATING_DEMAND = "heating_demand"
