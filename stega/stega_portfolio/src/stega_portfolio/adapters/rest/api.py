"""API entrypoint for stega portfolio service."""

import typing as T

from flask import Blueprint, request, Request

from stega_portfolio.adapters.rest.utils import ViewResponseType, ResponseType, get_bus
from stega_portfolio.domain.commands import CreatePortfolio
from stega_portfolio.views import portfolio as views
from stega_lib.domain import Command

api = Blueprint("portfolio_api", __name__)

@api.route("/portfolio/<string:portfolio_id>", methods=["GET"])
def get_portfolio(portfolio_id: str) -> ViewResponseType:
    bus = get_bus()
    view = views.get_portfolio(bus.uow)
    if view is None:
        return {
            "ok": False,
            "msg": f"Failed to find portfolio with id '{portfolio_id}'."
        }, 404

    return {
        "ok": True,
        "msg": f"Successfully found portfolio with id '{portfolio_id}'.",
        "view": view,
    }, 200


@api.route("/portfolios", methods=["GET"])
def get_portfolios() -> ViewResponseType:
    """Get a list of existing portfolios."""
    bus = get_bus()
    view = views.list_portfolios(bus.uow)
    return {
        "ok": True,
        "msg": "Successfully retrieved all portfolios.",
        "view": view,
    }, 200


@api.route("/portfolios", methods=["POST"])
def create_portfolio() -> ResponseType:
    """Create a new portfolio."""
    payload = request.get_json()
    if payload is None:
        return {"ok": False, "msg": "Failed to process request."}, 400

    bus = get_bus()
    correlation_id = _extract_correlation_id(request)
    cmd = _extract_create_portfolio_command(correlation_id, payload)
    bus.handle(cmd)
    return {
        "ok": True,
        "msg": f"Successfully created portfolio '{cmd.name}' with id '{cmd.id}'.",
        "id": cmd.id,
    }, 201


def _extract_correlation_id(request: Request) -> str:
    return request.headers.get("X-Request-Id", type=str, default=Command.gen_id())


def _extract_create_portfolio_command(
    correlation_id: str,
    payload: dict[str, T.Any],
) -> CreatePortfolio:
    if "name" not in payload:
        err_msg = "'name' is required for create portfolio request"
        raise ValueError(err_msg)
    name = payload["name"]

    if not isinstance(name, str):
        err_msg = "'name' must be a string for create portfolio request"
        raise TypeError(err_msg)

    assets = payload.get("assets", {})
    if not isinstance(assets, dict):
        err_msg = "'assets' must be a mapping type for create portfolio request"
        raise TypeError(err_msg)

    return CreatePortfolio(
        correlation_id=correlation_id,
        id=CreatePortfolio.gen_id(),
        name=name,
        assets=assets,
    )
