import functools
from dataclasses import asdict
from typing import Any

from stega_lib import http
from stega_lib.events import PortfolioCreated

from stega_cli.config import create_config
from stega_cli.domain.command import (
    CreatePortfolio,
    GetPortfolio,
    ListPortfolios,
)
from stega_cli.domain.request import Response
from stega_cli.ports import actions as actions_db
from stega_cli.ports import db
from stega_cli.ports import portfolio as portfolio_db
from stega_cli.services.handlers.sse import submit_and_wait_for_event


def list_portfolios(_: ListPortfolios) -> Response:
    """Handle listing all portfolios.

    Args:
        cmd: A ListPortfolios command instance.

    Returns:
        A Response instance with the portfolio list results.

    """
    config = create_config()
    with http.acquire_session(config.core_service_url) as session:
        resp = session.get("portfolios")
        data = resp.json()
    status = data["ok"]
    result = data["result"] if status else data["msg"]
    return Response(
        status="ok" if status else "error",
        result=result,
    )


def get_portfolio(cmd: GetPortfolio) -> Response:
    """Handle getting a portfolio.

    Args:
        cmd: A GetPortfolio command instance.

    Returns:
        A Response instance with the portfolio contents.

    """
    config = create_config()
    # check if portfolio is locally cached first
    with db.acquire_connection(config.db_path) as conn:
        portfolio = portfolio_db.get_portfolio(conn, cmd.portfolio_id)
        if portfolio is not None:
            return Response(
                status="ok",
                result=asdict(portfolio),
            )

    data = {}
    # hit api to get latest result
    with http.acquire_session(config.core_service_url) as session:
        resp = session.get(f"portfolio/{cmd.portfolio_id}")
        data = resp.json()

    status = data["ok"]
    result = data["result"] if status else data["msg"]
    return Response(
        status="ok" if status else "error",
        result=result,
    )


def create_portfolio_request(cmd: CreatePortfolio) -> None:
    """Submit request to create portfolio in core service.

    Args:
        cmd: A CreatePortfolio command instance.

    """
    config = create_config()
    with http.acquire_session(config.core_service_url) as session:
        payload = {
            "name": cmd.name,
            "assets": cmd.assets,
        }
        headers = {
            "X-Request-Id": cmd.correlation_id,
        }
        resp = session.post("portfolios", headers=headers, json=payload)
        resp.raise_for_status()


def create_portfolio(cmd: CreatePortfolio) -> None:
    """Handle creating a portfolio.

    NOTE: This will submit the request to create a portfolio and also wait
    for the corresponding PortfolioCreated event to be streamed with the
    resulting portfolios contents using the correlation id to match the initial
    request.

    Args:
        cmd: A CreatePortfolio command instance.

    """
    config = create_config()
    # submit request and wait for event to emit via SSE
    request_callback = functools.partial(create_portfolio_request, cmd=cmd)

    def matches(data: dict[str, Any]) -> bool:
        return cmd.correlation_id == data["correlation_id"]

    data = submit_and_wait_for_event(
        base_url=config.core_service_url,
        topic=PortfolioCreated.topic,
        matches=matches,
        request_callback=request_callback,
    )
    # update cache with portfolio data
    cache_local_portfolio(data)


def cache_local_portfolio(data: dict[str, Any]) -> None:
    """Store a portfolio's contents in a local cache.

    Args:
        data: A dict of the portfolio contents.

    """
    config = create_config()
    correlation_id = data["correlation_id"]
    portfolio_id = data["portfolio_id"]
    name = data["name"]
    assets = data["assets"]
    with db.acquire_connection(config.db_path) as conn:
        # record entity in portfolios
        portfolio_db.upsert_portfolio(
            conn,
            portfolio_id,
            name,
            assets,
        )
        # record entity in actions
        actions_db.insert_correlation(
            conn,
            correlation_id,
            portfolio_id,
        )
        conn.commit()
