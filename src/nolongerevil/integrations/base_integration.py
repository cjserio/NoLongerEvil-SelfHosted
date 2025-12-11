"""Base class for integrations."""

from abc import ABC, abstractmethod
from typing import Any

from nolongerevil.lib.types import DeviceStateChange, IntegrationConfig


class BaseIntegration(ABC):
    """Abstract base class for all integrations.

    Integrations receive notifications about device state changes
    and can perform actions like publishing to MQTT, sending webhooks, etc.
    """

    def __init__(self, config: IntegrationConfig) -> None:
        """Initialize the integration.

        Args:
            config: Integration configuration from database
        """
        self.config = config
        self.user_id = config.user_id
        self.type = config.type
        self._enabled = config.enabled

    @property
    def enabled(self) -> bool:
        """Check if integration is enabled."""
        return self._enabled

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the integration (connect to services, etc.)."""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the integration gracefully."""
        pass

    @abstractmethod
    async def on_device_state_change(self, change: DeviceStateChange) -> None:
        """Handle device state change notification.

        Args:
            change: State change event
        """
        pass

    @abstractmethod
    async def on_device_connected(self, serial: str) -> None:
        """Handle device connected notification.

        Args:
            serial: Device serial that connected
        """
        pass

    @abstractmethod
    async def on_device_disconnected(self, serial: str) -> None:
        """Handle device disconnected notification.

        Args:
            serial: Device serial that disconnected
        """
        pass

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self.config.config.get(key, default)
