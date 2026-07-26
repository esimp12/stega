from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from datetime import datetime

    from stega_market_data.domain.price import SymbolResult


class PriceProvider(Protocol):
    async def fetch_latest(self, tickers: list[str]) -> list[SymbolResult]: ...

    async def fetch_history(self, starts: dict[str, datetime], target: datetime) -> list[SymbolResult]: ...
