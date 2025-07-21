"""API entrypoint for stega portfolio service."""

import typing as T

from flask import Blueprint, request

from stega_portfolio.adapters.rest.utils import ResponseType, get_bus
from stega_portfolio.domain.commands import CreatePortfolio

api = Blueprint("portfolio_api", __name__)


@api.route("/portfolios", methods=["POST"])
def create_portfolio() -> ResponseType:
    """Create a new portfolio."""
    payload = request.get_json()
    if payload is None:
        return {"ok": False, "msg": "Failed to process request."}, 400

    bus = get_bus()
    cmd = _extract_create_portfolio_command(payload)
    bus.handle(cmd)
    return {
        "ok": True,
        "msg": f"Successfully created portfolio '{cmd.name}' with id '{cmd.id}'.",
        "id": cmd.id,
    }, 201


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
        id=CreatePortfolio.gen_id(),
        name=name,
        assets=assets,
    )
