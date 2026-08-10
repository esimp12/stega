import contextlib
import sqlite3
from collections.abc import Iterator

_TABLES = (
    # actions table
    """
    CREATE TABLE IF NOT EXISTS actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        correlation_id VARCHAR(36) NOT NULL,
        entity_id VARCHAR(36)
    )
    """,
    # portfolios table
    """
    CREATE TABLE IF NOT EXISTS portfolios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        portfolio_id VARCHAR(36) NOT NULL,
        name VARCHAR(255) NOT NULL,
        UNIQUE(portfolio_id)
    )
    """,
    # portfolio assets table
    """
    CREATE TABLE IF NOT EXISTS portfolio_assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        portfolio_id VARCHAR(36) NOT NULL,
        symbol VARCHAR(10) NOT NULL,
        weight REAL NOT NULL,
        UNIQUE (portfolio_id, symbol),
        FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id)
    )
    """,
)

_INDEXES = (
    # actions indexes
    """
    CREATE INDEX IF NOT EXISTS actions_correlation_id_index
    ON actions(correlation_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS actions_entity_id_index
    ON actions(correlation_id)
    """,
    # portfolios indexes
    """
    CREATE INDEX IF NOT EXISTS portfolios_portfolio_id_index
    ON portfolios(portfolio_id)
    """,
    # portfolio assets indexes
    """
    CREATE INDEX IF NOT EXISTS portfolio_assets_portfolio_id_symbol_index
    ON portfolio_assets(portfolio_id, symbol)
    """,
)


@contextlib.contextmanager
def acquire_connection(db_path: str) -> Iterator[sqlite3.Connection]:
    """Open a connection to the local cache.

    Args:
        db_path: A str of the path to the local cache.

    Yields:
        A sqlite3.Connection instance.

    """
    conn = sqlite3.connect(db_path)
    yield conn
    conn.close()


def init_db(db_path: str) -> None:
    """Initialize the local cache creating all tables and indexes.

    Args:
        db_path: A str of the path to the local cache.

    """
    with acquire_connection(db_path) as conn:
        cursor = conn.cursor()
        # create tables
        for table in _TABLES:
            cursor.execute(table)
        # create indexes
        for index in _INDEXES:
            cursor.execute(index)
        conn.commit()
