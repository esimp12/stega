from __future__ import annotations

from typing import TYPE_CHECKING

from stega_contracts.portfolio.event import (
    PortfolioCreated,
    PortfolioDeleted,
    PortfolioUpdated,
)

from stega_cli.ports.cache import portfolio as portfolio_db

if TYPE_CHECKING:
    import sqlite3
    from collections.abc import Callable

    from stega_core import Event


SUBSCRIPTIONS: list[type[Event]] = [
    PortfolioCreated,
    PortfolioUpdated,
    PortfolioDeleted,
]


def on_portfolio_created(conn: sqlite3.Connection, event: PortfolioCreated) -> None:
    portfolio_db.upsert_portfolio(conn, event.portfolio_id, event.name, event.assets)
    actions.insert_correlation(conn, event.correlation_id, event.portfolio_id)


def on_portfolio_deleted(conn: sqlite3.Connection, event: PortfolioDeleted) -> None:
    portfolio_db.delete(conn, event.portfolio_id)


def on_portfolio_updated(conn: sqlite3.Connection, event: PortfolioUpdated) -> None:
    portfolio_db.delete(conn, event.portfolio_id)
    actions.insert_correlation(conn, event.correlation_id, event.portfolio_id)


CACHE_HANDLERS: dict[type[Event], Callable[[sqlite3.Connection, Event], None]] = {
    PortfolioCreated: on_portfolio_created,
    PortfolioUpdated: on_portfolio_updated,
    PortfolioDeleted: on_portfolio_deleted,
}


def _read_get_portfolio(conn: sqlite3.Connection, query: GetPortfolio) -> dict | None:
    portfolio = portfolio_cache.get_portfolio(conn, query.portfolio_id)
    if portfolio is None:
        entity_id = actions.get_entity_id(conn, query.portfolio_id)
        if entity_id is not None:
            portfolio = portfolio_cache.get_portfolio(conn, entity_id)
    return None if portfolio is None else portfolio.asdict()


def _writeback_get_portfolio(conn: sqlite3.Connection, data: dict) -> None:
    portfolio_cache.insert_portfolio_if_absent(conn, data["portfolio_id"], data["name"], data["assets"])


CACHE_READERS = {
    GetPortfolio: _read_get_portfolio,
}
CACHE_WRITEBACKS = {
    GetPortfolio: _writeback_get_portfolio,
}
