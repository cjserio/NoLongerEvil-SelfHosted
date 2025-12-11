"""Nest entry endpoint - service discovery."""

from aiohttp import web

from nolongerevil.config import settings
from nolongerevil.lib.logger import get_logger

logger = get_logger(__name__)


async def handle_entry(request: web.Request) -> web.Response:
    """Handle Nest service discovery request.

    Returns URLs for all Nest services that the device needs to communicate with.

    Returns:
        JSON response with service URLs
    """
    origin = settings.api_origin

    # Build service URLs
    response_data = {
        "czfe_url": f"{origin}/nest/transport",
        "transport_url": f"{origin}/nest/transport",
        "direct_transport_url": f"{origin}/nest/transport",
        "passphrase_url": f"{origin}/nest/passphrase",
        "ping_url": f"{origin}/nest/transport",
        "pro_info_url": f"{origin}/nest/pro_info",
        "weather_url": f"{origin}/nest/weather/v1?query=",
        "upload_url": f"{origin}/nest/upload",
        "software_update_url": "",
        "server_version": "1.0.0",
        "tier_name": "local",
    }

    logger.debug(f"Entry request from {request.remote}")

    return web.json_response(response_data)


def create_entry_routes(app: web.Application) -> None:
    """Register entry routes.

    Args:
        app: aiohttp application
    """
    # Handle both GET and POST for /nest/entry - devices may use either
    app.router.add_get("/nest/entry", handle_entry)
    app.router.add_post("/nest/entry", handle_entry)
