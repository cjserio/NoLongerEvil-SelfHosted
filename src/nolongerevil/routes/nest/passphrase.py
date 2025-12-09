"""Nest passphrase endpoint - entry key generation for device pairing."""

from aiohttp import web

from nolongerevil.config import settings
from nolongerevil.lib.logger import get_logger
from nolongerevil.lib.serial_parser import extract_serial_from_request
from nolongerevil.services.device_state_service import DeviceStateService

logger = get_logger(__name__)


async def handle_passphrase(request: web.Request) -> web.Response:
    """Handle entry key generation request.

    Generates a unique pairing code for the requesting device.
    Uses deviceStateManager.generateEntryKey() to match TypeScript behavior.

    Returns:
        JSON response with entry key
    """
    # Extract device serial
    serial = extract_serial_from_request(request)
    if not serial:
        logger.warning("Passphrase request without valid serial")
        return web.json_response(
            {"error": "Device serial required"},
            status=400,
        )

    state_service: DeviceStateService = request.app["state_service"]
    ttl = settings.entry_key_ttl_seconds

    # Use generateEntryKey to handle code generation, expiration, and storage
    entry_key = await state_service.storage.generate_entry_key(serial, ttl)

    if not entry_key:
        logger.error(f"Failed to generate entry key for {serial}")
        return web.json_response(
            {"error": "Entry key service unavailable"},
            status=503,
        )

    logger.info(f"Generated entry key for {serial}: {entry_key.get('code')}")

    return web.json_response(
        {
            "value": entry_key.get("code"),
            "expires": entry_key.get("expiresAt"),
        }
    )


def create_passphrase_routes(
    app: web.Application,
    state_service: DeviceStateService,
) -> None:
    """Register passphrase routes.

    Args:
        app: aiohttp application
        state_service: Device state service
    """
    app["state_service"] = state_service
    app.router.add_get("/nest/passphrase", handle_passphrase)
