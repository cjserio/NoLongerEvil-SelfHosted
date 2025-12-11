"""Nest ping endpoint - health check."""

import time

from aiohttp import web

from nolongerevil.lib.logger import get_logger

logger = get_logger(__name__)


async def handle_ping(_request: web.Request) -> web.Response:
    """Handle Nest health check request.

    Returns:
        JSON response with status and timestamp
    """
    return web.json_response({"status": "ok", "timestamp": int(time.time() * 1000)})


def create_ping_routes(app: web.Application) -> None:
    """Register ping routes.

    Args:
        app: aiohttp application
    """
    app.router.add_get("/nest/ping", handle_ping)
