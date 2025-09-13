"""API entrypoint for stega core service."""

import typing as T

from flask import Blueprint, request

from stega_core.adapters.rest.utils import ResponseType, get_dispatcher
from stega_core.domain.commands import CreatePortfolio
from stega_core.services.handlers.portfolio import list_portfolios
from stega_core.ports.http import HttpRestPortfolioServicePort

api = Blueprint("core_portfolio_api", __name__)


@api.route("/portfolios", methods=["POST"])
def create_portfolio() -> ResponseType:
    """Create a new portfolio."""
    payload = request.get_json()
    if payload is None:
        return {"ok": False, "msg": "Failed to process request."}, 400

    dispatcher = get_dispatcher()
    cmd = _extract_create_portfolio_command(payload)
    result = dispatcher.handle(cmd)
    return {
        "ok": True,
        "msg": f"Successfully created portfolio '{cmd.name}' with result '{result}'.",
        "result": result,
    }, 201


@api.route("/portfolios", methods=["GET"])
def list_all_portfolios() -> ResponseType:
    """List all portfolios."""
    service = HttpRestPortfolioServicePort()
    portfolios = list_portfolios(service)
    return {
        "ok": True,
        "msg": "Successfully fetched all portfolios.",
        "result": portfolios,
    }, 200


def _extract_create_portfolio_command(payload: T.Mapping[str, T.Any]) -> CreatePortfolio:
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
        name=name,
        assets=assets,
    )
