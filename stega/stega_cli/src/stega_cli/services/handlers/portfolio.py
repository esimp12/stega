import json
from dataclasses import asdict

from stega_cli.config import create_config
from stega_cli.domain.command import GetPortfolio 
from stega_cli.domain.request import Response
from stega_cli.ports import db
from stega_cli.ports import portfolio as portfolio_db
from stega_cli.ports import actions as actions_db
from stega_lib import http
from stega_lib.events import PortfolioCreated


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


def create_portfolio(cmd: CreatePortfolio) -> None:
    config = create_config()

    # submit the portfolio creation request
    with http.acquire_session(config.core_service_url) as session:
        payload = {
            "name": cmd.name,
            "assets": cmd.assets,
        }
        resp = session.post("portfolios", json=payload)
        resp.raise_for_status()

    # TODO: need to subscribe to portfolio topic in background before we submit request
    # to create portfolio
    # subscribe to create portfolio topic and wait
    listen_for_create_portfolio_event(cmd.correlation_id)


def listen_for_create_portfolio_event(correlation_id: str) -> None:
    config = create_config()
    
    # subscribe to event and wait for result
    data = {}
    topic_url = f"events/{PortfolioCreated.topic}"
    with http.acquire_session(config.core_service_url, timeout=False) as session:
        with session.stream("GET", topic_url) as resp:
            for line in resp.iter_lines():
                if not line:
                    continue
                data = json.loads(line)
                print(correlation_id, data)
                msg_type = data["type"]
                # skip heartbeats
                if msg_type == "heartbeat":
                    continue
                # check if correlation id is present 
                if correlation_id == data["correlation_id"]:
                    # entity found so break
                    break

    print(data)
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

