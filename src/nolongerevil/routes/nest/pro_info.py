"""Nest pro_info endpoint - installer information lookup."""

from aiohttp import web

from nolongerevil.lib.logger import get_logger

logger = get_logger(__name__)


async def handle_pro_info(request: web.Request) -> web.Response:
    """Handle installer information lookup request.

    The {code} path parameter is typically a pro installer code.
    Since we're self-hosted, we return a generic response.

    Returns:
        JSON response with installer info (or empty)
    """
    code = request.match_info.get("code", "")

    logger.debug(f"Pro info request for code: {code}")

    # Return empty/default pro info
    return web.json_response(
        {
            "pro_id": code,
            "company_name": "Self-Hosted",
            "phone": "",
            "email": "",
        }
    )


def create_pro_info_routes(app: web.Application) -> None:
    """Register pro_info routes.

    Args:
        app: aiohttp application
    """
    app.router.add_get("/nest/pro_info/{code}", handle_pro_info)
