"""Control API routes module."""

from aiohttp import web

from nolongerevil.services.device_availability import DeviceAvailability
from nolongerevil.services.device_state_service import DeviceStateService
from nolongerevil.services.subscription_manager import SubscriptionManager

from .command import create_command_routes
from .status import create_status_routes


def setup_control_routes(
    app: web.Application,
    state_service: DeviceStateService,
    subscription_manager: SubscriptionManager,
    device_availability: DeviceAvailability,
) -> None:
    """Set up all Control API routes.

    Args:
        app: aiohttp application
        state_service: Device state service
        subscription_manager: Subscription manager
        device_availability: Device availability service
    """
    create_command_routes(app, state_service, subscription_manager)
    create_status_routes(app, state_service, subscription_manager, device_availability)


__all__ = [
    "setup_control_routes",
    "create_command_routes",
    "create_status_routes",
]
