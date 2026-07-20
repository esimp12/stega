from __future__ import annotations

from datetime import datetime
from typing import Protocol

from stega_market_data.domain.price import SymbolResult


class PriceProvider(Protocol):

    async def fetch_latest(self, tickers: list[str]) -> list[SymbolResult]:
        ...

    async def fetch_history(self, starts: dict[str, datetime], target: datetime) -> list[SymbolResult]:
        ...
