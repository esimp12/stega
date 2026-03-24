import functools
import json
from dataclasses import asdict

from stega_cli.config import create_config
from stega_cli.domain.command import (
    CreatePortfolio,
    GetPortfolio,
    ListPortfolios,
)
from stega_cli.domain.request import Response
from stega_cli.ports import db
from stega_cli.ports import portfolio as portfolio_db
from stega_cli.ports import actions as actions_db
from stega_cli.services.handlers.sse import submit_and_wait_for_event
from stega_lib import http
from stega_lib.events import PortfolioCreated


def list_portfolios(cmd: ListPortfolios) -> Response:
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

    # TODO: cache result locally if found

    return Response(
        status="ok" if status else "error",
        result=result,
    )


def create_portfolio_request(cmd: CreatePortfolio) -> None:
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
    config = create_config()
    # submit request and wait for event to emit via SSE
    request_callback = functools.partial(create_portfolio_request, cmd=cmd)

    def matches(data: dict[str, T.Any]) -> bool:
        return cmd.correlation_id == data["correlation_id"]

    data = submit_and_wait_for_event(
        base_url=config.core_service_url,
        topic=PortfolioCreated.topic,
        matches=matches,
        request_callback=request_callback,
    )
    # update cache with portfolio data
    cache_local_portfolio(data)


def cache_local_portfolio(data: dict[str, T.Any]) -> None:
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

