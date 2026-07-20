from enum import StrEnum

from stega_core import Command


class PullKind(StrEnum):
    LATEST = "latest"
    BACKFILL = "backfill"


class PullPrices(Command):
    kind: PullKind
    tickers: list[str]
