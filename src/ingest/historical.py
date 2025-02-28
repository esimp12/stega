import asyncio
import typing as T
from datetime import date, datetime

import httpx

from config import CONFIG
from src import http


async def historical_prices(
    session: httpx.AsyncClient,
    symbols: T.List[T.Tuple[int, str]],
) -> T.AsyncGenerator[T.List[T.Tuple[date, str, float]], None]:
    tasks = create_tasks(session, symbols)
    for result in asyncio.as_completed(tasks):
        quotes = await result
        yield quotes


def create_tasks(
    session: httpx.AsyncClient,
    symbols: T.List[T.Tuple[int, str]],
) -> T.List[asyncio.Task]:
    rate = http.RateLimiter(CONFIG.STEGA_EOD_API_MAX, CONFIG.STEGA_EOD_API_PERIOD)
    tasks = []
    for symbol_id, symbol in symbols:
        coro = quote_coroutine(rate, session, symbol_id, symbol)
        task = asyncio.create_task(coro)
        tasks.append(task)
    return tasks


async def quote_coroutine(
    rate: http.RateLimiter,
    session: httpx.AsyncClient,
    symbol_id: int,
    symbol: str,
) -> T.Awaitable[T.List[T.Tuple[date, int, float]]]:
    url = f"/eod/{symbol}.{CONFIG.STEGA_EOD_EXCHANGE}"
    response = await http.fetch(rate, session, url)
    data = response.json()
    return map_eod_quotes(symbol_id, data)


def map_eod_quotes(
    symbol_id: int,
    quotes: T.List[T.Dict[str, T.Any]],
) -> T.List[T.Tuple[date, int, float]]:
    return [
        (
            parse_date(quote["date"]),
            symbol_id,
            quote["close"],
        )
        for quote in quotes
    ]


def parse_date(d: str) -> date:
    return datetime.strptime(d, CONFIG.STEGA_EOD_DATEFMT).date()
