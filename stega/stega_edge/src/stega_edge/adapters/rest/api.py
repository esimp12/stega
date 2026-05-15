from quart import Blueprint, Request, request

from stega_edge.adapters.rest.utils import ResponseType, get_bus
from stega_edge.domain.command import CreatePortfolio
from stega_edge.domain.query import GetPortfolio, ListPortfolios

api = Blueprint("edge_portfolio_api", __name__)


@api.route("/portfolio/<string:portfolio_id>", methods=["GET"])
async def get_portfolio(portfolio_id: str) -> ResponseType:
    query = GetPortfolio(portfolio_id)
    bus = get_bus()
    resp = await bus.handle_query(query)
    return {
        "ok": resp.ok,
        "msg": f"Successfully found portfolio with id '{portfolio_id}'.",
        "result": resp.result,
    }, 200


@api.route("/portfolios", methods=["POST"])
async def create_portfolio() -> ResponseType:
    payload = request.get_json()
    if payload is None:
        return {"ok": False, "msg": "Failed to process request."}, 400

    correlation_id = _extract_correlation_id(request)
    cmd = _extract_create_portfolio_command(correlation_id, payload)
    bus = get_bus()
    resp = await bus.handle(cmd)
    return {
        "ok": resp.ok,
        "msg": f"Submitted request to create portfolio with status '{resp.status!r}'.",
        "result": resp.result,
    }, 201


@api.route("/portfolios", methods=["GET"])
async def list_all_portfolios() -> ResponseType:
    query = ListPortfolios()
    bus = get_bus()
    resp = await bus.handle_query(query)
    return {
        "ok": resp.ok,
        "msg": "Successfully fetched all portfolios.",
        "result": resp.result,
    }, 200


def _extract_correlation_id(request: Request) -> str:
    return request.headers.get("X-Request-Id", type=str)


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
