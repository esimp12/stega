"""API entrypoint for stega core service."""

from flask import Blueprint, request, Request

from stega_core.adapters.rest.utils import ResponseType, get_dispatcher
from stega_core.domain.commands import CreatePortfolio
from stega_core.services.handlers import portfolio as handlers 
from stega_core.ports.http import HttpRestPortfolioServicePort
from stega_lib.domain import Command

api = Blueprint("core_portfolio_api", __name__)


@api.route("/portfolio/<string:portfolio_id>", methods=["GET"])
def get_portfolio(portfolio_id: str) -> ResponseType:
    """Get an existing portfolio."""
    service = HttpRestPortfolioServicePort()
    portfolio = handler.get_portfolio(service)
    if portfolio is None:
        return {
            "ok": False,
            "msg": f"Failed to find portfolio with id '{portfolio_id}'.",
        }, 404

    return {
        "ok": True,
        "msg": f"Successfully found portfolio with id '{portfolio_id}'.",
        "result": portfolio,
    }, 200


@api.route("/portfolios", methods=["POST"])
def create_portfolio() -> ResponseType:
    """Create a new portfolio."""
    payload = request.get_json()
    if payload is None:
        return {"ok": False, "msg": "Failed to process request."}, 400

    dispatcher = get_dispatcher()
    correlation_id = _extract_correlation_id(request)
    cmd = _extract_create_portfolio_command(correlation_id, payload)
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
    portfolios = handlers.list_portfolios(service)
    return {
        "ok": True,
        "msg": "Successfully fetched all portfolios.",
        "result": portfolios,
    }, 200


def _extract_correlation_id(request: Request) -> str:
    return request.headers.get("X-Request-Id", type=str, default=Command.gen_id())


def _extract_create_portfolio_command(
    correlation_id: str,
    payload: dict[str, str | dict[str, float]],
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
        name=name,
        assets=assets,
    )
