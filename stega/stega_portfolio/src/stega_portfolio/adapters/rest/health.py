from quart import Blueprint

from stega_portfolio.adapters.rest.utils import ResponseType

api = Blueprint("health_api", __name__)


@api.route("/health", methods=["GET"])
async def health() -> ResponseType:
    return {
        "ok": True,
        "msg": "Portfolio service is healthy!",
    }, 200
