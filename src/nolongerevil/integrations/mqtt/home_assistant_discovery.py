"""Home Assistant MQTT discovery message generation.

Reference: https://www.home-assistant.io/integrations/mqtt/#mqtt-discovery

Discovery Topic Format:
<discovery_prefix>/<component>/[<node_id>/]<object_id>/config

Example:
homeassistant/climate/nest_02AA01AC/thermostat/config
"""

from typing import Any

from nolongerevil.integrations.mqtt.helpers import get_device_name


def build_climate_discovery_payload(
    serial: str,
    device_name: str,
    topic_prefix: str,
) -> dict[str, Any]:
    """Build Home Assistant climate discovery payload.

    Always uses Celsius - HA handles display conversion based on user preferences.
    This avoids double-conversion bugs when Nest display unit changes.

    Args:
        serial: Device serial
        device_name: Human-readable device name
        topic_prefix: MQTT topic prefix

    Returns:
        Discovery payload dictionary
    """
    return {
        # Unique identifier
        "unique_id": f"nolongerevil_{serial}",
        # Device name
        "name": device_name,
        # Object ID (used for entity naming)
        "object_id": f"nest_{serial}",
        # Device info (groups all entities together)
        "device": {
            "identifiers": [f"nolongerevil_{serial}"],
            "name": device_name,
            "model": "Nest Thermostat",
            "manufacturer": "Google Nest",
            "sw_version": "NoLongerEvil",
        },
        # Availability topic
        "availability": {
            "topic": f"{topic_prefix}/{serial}/availability",
            "payload_available": "online",
            "payload_not_available": "offline",
        },
        # Temperature unit - always Celsius (Nest internal format)
        # HA will convert to user's display preference automatically
        "temperature_unit": "C",
        # Precision (0.5 for Nest)
        "precision": 0.5,
        "temp_step": 0.5,
        # Current temperature
        "current_temperature_topic": f"{topic_prefix}/{serial}/ha/current_temperature",
        # Current humidity
        "current_humidity_topic": f"{topic_prefix}/{serial}/ha/current_humidity",
        # Target temperature (heat/cool mode)
        "temperature_command_topic": f"{topic_prefix}/{serial}/ha/target_temperature/set",
        "temperature_state_topic": f"{topic_prefix}/{serial}/ha/target_temperature",
        # Target temperature high (auto mode)
        "temperature_high_command_topic": f"{topic_prefix}/{serial}/ha/target_temperature_high/set",
        "temperature_high_state_topic": f"{topic_prefix}/{serial}/ha/target_temperature_high",
        # Target temperature low (auto mode)
        "temperature_low_command_topic": f"{topic_prefix}/{serial}/ha/target_temperature_low/set",
        "temperature_low_state_topic": f"{topic_prefix}/{serial}/ha/target_temperature_low",
        # HVAC mode (heat, cool, heat_cool, off)
        "mode_command_topic": f"{topic_prefix}/{serial}/ha/mode/set",
        "mode_state_topic": f"{topic_prefix}/{serial}/ha/mode",
        "modes": ["off", "heat", "cool", "heat_cool"],
        # HVAC action (heating, cooling, idle, fan, off)
        "action_topic": f"{topic_prefix}/{serial}/ha/action",
        # Fan mode (on, auto)
        "fan_mode_command_topic": f"{topic_prefix}/{serial}/ha/fan_mode/set",
        "fan_mode_state_topic": f"{topic_prefix}/{serial}/ha/fan_mode",
        "fan_modes": ["auto", "on"],
        # Preset modes (home, away, eco)
        "preset_mode_command_topic": f"{topic_prefix}/{serial}/ha/preset/set",
        "preset_mode_state_topic": f"{topic_prefix}/{serial}/ha/preset",
        "preset_modes": ["home", "away", "eco"],
        # Min/max temperature in Celsius (typical Nest range)
        "min_temp": 9,
        "max_temp": 32,
        # Optimistic mode
        "optimistic": False,
        # QoS
        "qos": 1,
    }


def build_temperature_sensor_discovery(
    serial: str,
    topic_prefix: str,
) -> dict[str, Any]:
    """Build Home Assistant discovery payload for temperature sensor."""
    return {
        "unique_id": f"nolongerevil_{serial}_temperature",
        "name": "Temperature",
        "object_id": f"nest_{serial}_temperature",
        "device": {
            "identifiers": [f"nolongerevil_{serial}"],
        },
        "state_topic": f"{topic_prefix}/{serial}/ha/current_temperature",
        "unit_of_measurement": "°C",
        "device_class": "temperature",
        "state_class": "measurement",
        "availability": {
            "topic": f"{topic_prefix}/{serial}/availability",
            "payload_available": "online",
            "payload_not_available": "offline",
        },
        "qos": 0,
    }


def build_humidity_sensor_discovery(
    serial: str,
    topic_prefix: str,
) -> dict[str, Any]:
    """Build Home Assistant discovery payload for humidity sensor."""
    return {
        "unique_id": f"nolongerevil_{serial}_humidity",
        "name": "Humidity",
        "object_id": f"nest_{serial}_humidity",
        "device": {
            "identifiers": [f"nolongerevil_{serial}"],
        },
        "state_topic": f"{topic_prefix}/{serial}/ha/current_humidity",
        "unit_of_measurement": "%",
        "device_class": "humidity",
        "state_class": "measurement",
        "availability": {
            "topic": f"{topic_prefix}/{serial}/availability",
            "payload_available": "online",
            "payload_not_available": "offline",
        },
        "qos": 0,
    }


def build_outdoor_temperature_sensor_discovery(
    serial: str,
    topic_prefix: str,
) -> dict[str, Any]:
    """Build Home Assistant discovery payload for outdoor temperature sensor."""
    return {
        "unique_id": f"nolongerevil_{serial}_outdoor_temperature",
        "name": "Outdoor Temperature",
        "object_id": f"nest_{serial}_outdoor_temperature",
        "device": {
            "identifiers": [f"nolongerevil_{serial}"],
        },
        "state_topic": f"{topic_prefix}/{serial}/ha/outdoor_temperature",
        "unit_of_measurement": "°C",
        "device_class": "temperature",
        "state_class": "measurement",
        "availability": {
            "topic": f"{topic_prefix}/{serial}/availability",
            "payload_available": "online",
            "payload_not_available": "offline",
        },
        "qos": 0,
    }


def build_occupancy_binary_sensor_discovery(
    serial: str,
    topic_prefix: str,
) -> dict[str, Any]:
    """Build Home Assistant discovery payload for occupancy binary sensor."""
    return {
        "unique_id": f"nolongerevil_{serial}_occupancy",
        "name": "Occupancy",
        "object_id": f"nest_{serial}_occupancy",
        "device": {
            "identifiers": [f"nolongerevil_{serial}"],
        },
        "state_topic": f"{topic_prefix}/{serial}/ha/occupancy",
        "payload_on": "home",
        "payload_off": "away",
        "device_class": "occupancy",
        "availability": {
            "topic": f"{topic_prefix}/{serial}/availability",
            "payload_available": "online",
            "payload_not_available": "offline",
        },
        "qos": 0,
    }


def build_fan_binary_sensor_discovery(
    serial: str,
    topic_prefix: str,
) -> dict[str, Any]:
    """Build Home Assistant discovery payload for fan binary sensor."""
    return {
        "unique_id": f"nolongerevil_{serial}_fan",
        "name": "Fan",
        "object_id": f"nest_{serial}_fan",
        "device": {
            "identifiers": [f"nolongerevil_{serial}"],
        },
        "state_topic": f"{topic_prefix}/{serial}/ha/fan_running",
        "payload_on": "true",
        "payload_off": "false",
        "device_class": "running",
        "availability": {
            "topic": f"{topic_prefix}/{serial}/availability",
            "payload_available": "online",
            "payload_not_available": "offline",
        },
        "qos": 0,
    }


def build_leaf_binary_sensor_discovery(
    serial: str,
    topic_prefix: str,
) -> dict[str, Any]:
    """Build Home Assistant discovery payload for leaf (eco) binary sensor."""
    return {
        "unique_id": f"nolongerevil_{serial}_leaf",
        "name": "Eco Mode",
        "object_id": f"nest_{serial}_leaf",
        "device": {
            "identifiers": [f"nolongerevil_{serial}"],
        },
        "state_topic": f"{topic_prefix}/{serial}/ha/eco",
        "payload_on": "true",
        "payload_off": "false",
        "device_class": "power",
        "availability": {
            "topic": f"{topic_prefix}/{serial}/availability",
            "payload_available": "online",
            "payload_not_available": "offline",
        },
        "qos": 0,
    }


def build_battery_sensor_discovery(
    serial: str,
    topic_prefix: str,
) -> dict[str, Any]:
    """Build Home Assistant discovery payload for battery sensor."""
    return {
        "unique_id": f"nolongerevil_{serial}_battery",
        "name": "Battery",
        "object_id": f"nest_{serial}_battery",
        "device": {
            "identifiers": [f"nolongerevil_{serial}"],
        },
        "state_topic": f"{topic_prefix}/{serial}/ha/battery",
        "unit_of_measurement": "%",
        "device_class": "battery",
        "state_class": "measurement",
        "availability": {
            "topic": f"{topic_prefix}/{serial}/availability",
            "payload_available": "online",
            "payload_not_available": "offline",
        },
        "qos": 0,
    }


def get_all_discovery_configs(
    serial: str,
    device_values: dict[str, Any],
    shared_values: dict[str, Any],
    topic_prefix: str,
    discovery_prefix: str = "homeassistant",
) -> list[tuple[str, dict[str, Any]]]:
    """Get all discovery configurations for a thermostat.

    Args:
        serial: Device serial
        device_values: Device object values
        shared_values: Shared object values
        topic_prefix: MQTT topic prefix
        discovery_prefix: HA discovery prefix (default: homeassistant)

    Returns:
        List of (topic, payload) tuples for all entities
    """
    device_name = get_device_name(device_values, shared_values, serial)
    configs = []

    # Climate entity (main thermostat control)
    climate_topic = f"{discovery_prefix}/climate/nest_{serial}/thermostat/config"
    climate_payload = build_climate_discovery_payload(serial, device_name, topic_prefix)
    configs.append((climate_topic, climate_payload))

    # Temperature sensor
    temp_topic = f"{discovery_prefix}/sensor/nest_{serial}/temperature/config"
    temp_payload = build_temperature_sensor_discovery(serial, topic_prefix)
    configs.append((temp_topic, temp_payload))

    # Humidity sensor
    humidity_topic = f"{discovery_prefix}/sensor/nest_{serial}/humidity/config"
    humidity_payload = build_humidity_sensor_discovery(serial, topic_prefix)
    configs.append((humidity_topic, humidity_payload))

    # Outdoor temperature sensor
    outdoor_temp_topic = f"{discovery_prefix}/sensor/nest_{serial}/outdoor_temperature/config"
    outdoor_temp_payload = build_outdoor_temperature_sensor_discovery(serial, topic_prefix)
    configs.append((outdoor_temp_topic, outdoor_temp_payload))

    # Occupancy binary sensor
    occupancy_topic = f"{discovery_prefix}/binary_sensor/nest_{serial}/occupancy/config"
    occupancy_payload = build_occupancy_binary_sensor_discovery(serial, topic_prefix)
    configs.append((occupancy_topic, occupancy_payload))

    # Fan binary sensor
    fan_topic = f"{discovery_prefix}/binary_sensor/nest_{serial}/fan/config"
    fan_payload = build_fan_binary_sensor_discovery(serial, topic_prefix)
    configs.append((fan_topic, fan_payload))

    # Leaf (eco) binary sensor
    leaf_topic = f"{discovery_prefix}/binary_sensor/nest_{serial}/leaf/config"
    leaf_payload = build_leaf_binary_sensor_discovery(serial, topic_prefix)
    configs.append((leaf_topic, leaf_payload))

    # Battery sensor
    battery_topic = f"{discovery_prefix}/sensor/nest_{serial}/battery/config"
    battery_payload = build_battery_sensor_discovery(serial, topic_prefix)
    configs.append((battery_topic, battery_payload))

    return configs


def get_discovery_removal_topics(
    serial: str,
    discovery_prefix: str = "homeassistant",
) -> list[str]:
    """Get all discovery topics for removing a device.

    Args:
        serial: Device serial
        discovery_prefix: HA discovery prefix

    Returns:
        List of discovery topics to clear
    """
    return [
        f"{discovery_prefix}/climate/nest_{serial}/thermostat/config",
        f"{discovery_prefix}/sensor/nest_{serial}/temperature/config",
        f"{discovery_prefix}/sensor/nest_{serial}/humidity/config",
        f"{discovery_prefix}/sensor/nest_{serial}/outdoor_temperature/config",
        f"{discovery_prefix}/sensor/nest_{serial}/battery/config",
        f"{discovery_prefix}/binary_sensor/nest_{serial}/occupancy/config",
        f"{discovery_prefix}/binary_sensor/nest_{serial}/fan/config",
        f"{discovery_prefix}/binary_sensor/nest_{serial}/leaf/config",
    ]
