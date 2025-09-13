"""API health entrypoint for stega portfolio service."""

from flask import Blueprint

from stega_portfolio.adapters.rest.utils import ResponseType

api = Blueprint("health_api", __name__)


@api.route("/health", methods=["GET"])
def health() -> ResponseType:
    """Get the current health of the service."""
    return {
        "ok": True,
        "msg": "Portfolio service is healthy!",
    }, 200


