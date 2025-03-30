import asyncio
import typing as T

import httpx

from config import CONFIG
from src import db, http
from src.ingest.historical import historical_prices
from src.ingest.symbols import symbols


def main():
    asyncio.run(run_job())


async def run_job():
    conn = db.connection(
        CONFIG.STEGA_DBNAME,
        CONFIG.STEGA_DBUSER,
        CONFIG.STEGA_DBPASSWORD,
        CONFIG.STEGA_DBHOST,
        CONFIG.STEGA_DBPORT,
    )
    update_symbols(conn)
    base_url = CONFIG.STEGA_EOD_API
    params = {
        "fmt": "json",
        "api_token": CONFIG.STEGA_EOD_API_TOKEN,
    }
    async with http.acquire_session(base_url, params) as session:
        await update_prices(conn, session)
    conn.close()


def update_symbols(conn):
    latest_symbols = symbols()
    db.create_symbols_table(conn)
    db.insert_symbols(conn, latest_symbols)


async def update_prices(conn, session: httpx.AsyncClient):
    db.create_prices_table(conn)
    latest_symbols = current_symbols(conn)
    async for eod_quotes in historical_prices(session, latest_symbols):
        db.insert_prices(conn, eod_quotes)


def current_symbols(conn) -> T.List[T.Tuple[int, str]]:
    rows = db.get_symbols(conn, CONFIG.STEGA_TEST_SYMBOLS)
    return [(row["id"], row["symbol"]) for row in rows]
