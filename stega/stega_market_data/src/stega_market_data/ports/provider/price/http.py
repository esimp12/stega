import asyncio
from datetime import datetime
from decimal import Decimal

import httpx

from stega_core import HttpProviderChannel
from stega_market_data.domain.price import SymbolResult


class HttpPriceProvider:

    def __init__(
        self,
        channel: HttpProviderChannel,
        api_key: str,
    ) -> None:
        self._channel = channel
        self._api_key = api_key

    async def start(self) -> None:
        await self._channel.start()

    async def stop(self) -> None:
        await self._channel.stop()

    async def _get(self, path: str, **params: dict) -> dict:
        params = {**params, "api_token": self._api_key, "fmt": "json"}
        resp = await self._channel.get(path, params=params)
        return resp.json()

    async def fetch_latest(self, tickers: list[str]) -> list[SymbolResult]:
        params = {"symbols": ",".join(tickers)}
        payload = await self._get("/eod-bulk-last-day/US", params)
        by_ticker = self._parse_latest(payload)
        return [
            SymbolResult(
                ticker=t,
                prices=by_ticker.get(t, []),
            )
            for t in tickers
        ]

    async def fetch_history(self, starts: dict[str, datetime], target: datetime) -> list[SymbolResult]:
        return list(await asyncio.gather(
            *(self._history_request(ticker, start, target) for ticker, start in starts.items()),
        ))

    async def _history_request(self, ticker: str, start: datetime, target: datetime) -> SymbolResult:
        params = {
            "from": start.strftime("%Y-%m-%d"),
            "to": target.strftime("%Y-%m-%d"),
        }
        payload = await self._get(f"/eod/{ticker}.US", params)
        return SymbolResult(
            ticker=ticker,
            prices=self._parse_history(ticker, payload)
        )

    def _parse_latest(self, payload: dict) -> dict[str, list[Price]]:
        return {
            record["code"]: [
                Price(
                    ticker=record["code"],
                    dt=datetime.strptime(record["date"], "%Y-%m-%d"),
                    amount=Decimal(record["close"]),
                ),
            ] 
            for record in payload
        }

    def _parse_history(self, ticker: str, payload: dict) -> list[Price]:
        return [
            Price(
                ticker=ticker,
                dt=datetime.strptime(record["date"], "%Y-%m-%d"),
                amount=Decimal(record["close"]),
            )
            for record in payload
        ]
