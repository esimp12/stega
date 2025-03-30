import typing as T
from datetime import date
from itertools import chain

import psycopg2
from psycopg2.extras import RealDictCursor, execute_values


def connection(dbname: str, username: str, password: str, host: str, port: int):
    return psycopg2.connect(
        f"dbname={dbname} user={username} password={password} host={host} port={port}"
    )


def create_symbols_table(conn):
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS symbols (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR NOT NULL,
            UNIQUE(symbol)
        );
        """
    )
    cur.close()
    conn.commit()


def insert_symbols(conn, symbols: T.List[str]):
    cur = conn.cursor()
    values = ",\n".join(f"('{symbol}')" for symbol in symbols)
    cur.execute(
        f"""
        INSERT INTO symbols (symbol) VALUES
        {values}
        ON CONFLICT (symbol) DO NOTHING;
        """
    )
    cur.close()
    conn.commit()


def get_symbols(
    conn, symbols: T.List[str] = None, limit: int = None, offset: int = None
) -> T.List[T.Dict[str, T.Any]]:
    cur = conn.cursor(cursor_factory=RealDictCursor)
    stmt = """
           SELECT id, symbol FROM symbols
           """
    if symbols:
        condition = ", ".join(f"'{s}'" for s in symbols)
        stmt += f"\nWHERE symbol IN ({condition})"
    if limit:
        stmt += f"\nLIMIT {limit}"
    if offset:
        stmt += f"\nOFFSET {offset}"
    stmt += ";"
    cur.execute(stmt)
    results = cur.fetchall()
    cur.close()
    return results


def create_prices_table(conn):
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS prices (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            symbol_id SERIAL REFERENCES symbols(id) NOT NULL,
            closing_price MONEY NOT NULL,
            UNIQUE(date, symbol_id)
        );
        """
    )
    cur.close()
    conn.commit()


def insert_prices(conn, quotes: T.List[T.Tuple[date, int, float]]):
    cur = conn.cursor()
    execute_values(
        cur,
        """
        INSERT INTO prices (date, symbol_id, closing_price)
        VALUES
        %s
        ON CONFLICT (date, symbol_id) DO NOTHING;
        """,
        quotes,
    )
    cur.close()
    conn.commit()


def get_prices(conn, symbol: str) -> T.List[T.Dict[str, T.Any]]:
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        SELECT date, symbol, closing_price::money::numeric::float8 FROM prices
        RIGHT JOIN symbols
        ON prices.symbol_id = symbols.id
        WHERE symbol = %s;
        """,
        (symbol,),
    )
    results = cur.fetchall()
    cur.close()
    return results


def flatten(iterable: T.Iterable) -> T.Generator:
    return chain.from_iterable(iterable)
