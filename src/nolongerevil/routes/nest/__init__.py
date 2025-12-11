"""Nest API routes module."""

from aiohttp import web

from nolongerevil.services.device_availability import DeviceAvailability
from nolongerevil.services.device_state_service import DeviceStateService
from nolongerevil.services.subscription_manager import SubscriptionManager
from nolongerevil.services.weather_service import WeatherService

from .entry import create_entry_routes
from .passphrase import create_passphrase_routes
from .ping import create_ping_routes
from .pro_info import create_pro_info_routes
from .transport import create_transport_routes
from .upload import create_upload_routes
from .weather import create_weather_routes


def setup_nest_routes(
    app: web.Application,
    state_service: DeviceStateService,
    subscription_manager: SubscriptionManager,
    weather_service: WeatherService,
    device_availability: DeviceAvailability,
) -> None:
    """Set up all Nest API routes.

    Args:
        app: aiohttp application
        state_service: Device state service
        subscription_manager: Subscription manager
        weather_service: Weather service
        device_availability: Device availability service
    """
    create_entry_routes(app)
    create_ping_routes(app)
    create_passphrase_routes(app, state_service)
    create_pro_info_routes(app)
    create_transport_routes(app, state_service, subscription_manager, device_availability)
    create_upload_routes(app)
    create_weather_routes(app, weather_service)


__all__ = [
    "setup_nest_routes",
    "create_entry_routes",
    "create_passphrase_routes",
    "create_ping_routes",
    "create_pro_info_routes",
    "create_transport_routes",
    "create_upload_routes",
    "create_weather_routes",
]
