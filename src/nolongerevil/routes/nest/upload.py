"""Nest upload endpoint - device log file upload."""

from aiohttp import web

from nolongerevil.lib.logger import get_logger
from nolongerevil.lib.serial_parser import extract_serial_from_request

logger = get_logger(__name__)


async def handle_upload(request: web.Request) -> web.Response:
    """Handle device log file upload.

    Devices may upload diagnostic logs. We acknowledge receipt
    but don't necessarily store them unless debug logging is enabled.

    Returns:
        Success response
    """
    serial = extract_serial_from_request(request)

    # Read the upload data (but we don't store it by default)
    try:
        data = await request.read()
        size = len(data)
        logger.info(f"Received log upload from device {serial or 'unknown'}: {size} bytes")
    except Exception as e:
        logger.warning(f"Failed to read upload data: {e}")

    return web.json_response({"status": "ok"})


def create_upload_routes(app: web.Application) -> None:
    """Register upload routes.

    Args:
        app: aiohttp application
    """
    app.router.add_post("/nest/upload", handle_upload)
