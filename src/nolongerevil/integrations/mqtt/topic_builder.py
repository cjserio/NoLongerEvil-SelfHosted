"""MQTT topic builder utilities."""

import re


def parse_object_key(object_key: str) -> tuple[str, str]:
    """Parse an object key into type and serial.

    Args:
        object_key: Object key (e.g., "device.SERIAL123")

    Returns:
        Tuple of (object_type, serial)
    """
    parts = object_key.split(".", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return object_key, ""


def build_state_topic(prefix: str, serial: str, object_type: str, field: str | None = None) -> str:
    """Build a state topic.

    Args:
        prefix: Topic prefix
        serial: Device serial
        object_type: Object type (device, shared, etc.)
        field: Field name (optional - if None, returns base topic for full object)

    Returns:
        Topic string
    """
    if field:
        return f"{prefix}/{serial}/{object_type}/{field}"
    return f"{prefix}/{serial}/{object_type}"


def build_command_topic(prefix: str, serial: str, object_type: str, field: str) -> str:
    """Build a command topic.

    Args:
        prefix: Topic prefix
        serial: Device serial
        object_type: Object type
        field: Field name

    Returns:
        Command topic string
    """
    return f"{prefix}/{serial}/{object_type}/{field}/set"


def build_availability_topic(prefix: str, serial: str) -> str:
    """Build an availability topic.

    Args:
        prefix: Topic prefix
        serial: Device serial

    Returns:
        Availability topic string
    """
    return f"{prefix}/{serial}/availability"


def build_command_pattern(prefix: str) -> str:
    """Build a pattern for subscribing to all command topics.

    Args:
        prefix: Topic prefix

    Returns:
        MQTT subscription pattern
    """
    return f"{prefix}/+/+/+/set"


def parse_command_topic(prefix: str, topic: str) -> tuple[str, str, str] | None:
    """Parse a command topic into components.

    Args:
        prefix: Expected topic prefix
        topic: Full topic string

    Returns:
        Tuple of (serial, object_type, field) or None if invalid
    """
    pattern = rf"^{re.escape(prefix)}/([^/]+)/([^/]+)/([^/]+)/set$"
    match = re.match(pattern, topic)

    if match:
        return match.group(1), match.group(2), match.group(3)
    return None
