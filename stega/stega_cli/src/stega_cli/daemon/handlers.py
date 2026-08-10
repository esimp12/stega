from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING

from stega_contracts.portfolio.event import (
    PortfolioCreated,
    PortfolioUpdated,
    PortfolioDeleted,
)

from stega_cli.ports.cache import portfolio as portfolio_db

if TYPE_CHECKING:
    from collections.abc import Callable

    from stega_core import Event


SUBSCRIPTIONS: list[type[Event]] = [
    PortfolioCreated,
    PortfolioUpdated,
    PortfolioDeleted,
]


def on_portfolio_created(conn: sqlite3.Connection, event: PortfolioCreated) -> None:
    portfolio_db.upsert(conn, event.portfolio_id, event.name, event.assets)


def on_portfolio_deleted(conn: sqlite3.Connection, event: PortfolioDeleted) -> None:
    portfolio_db.delete(conn, event.portfolio_id)


def on_portfolio_updated(conn: sqlite3.Connection, event: PortfolioUpdated) -> None:
    portfolio_db.delete(conn, event.portfolio_id)


CACHE_HANDLERS: dict[type[Event], Callable[[sqlite3.Connection, Event], None]] = {
    PortfolioCreated: on_portfolio_created,
    PortfolioUpdated: on_portfolio_updated,
    PortfolioDeleted: on_portfolio_deleted,
}
