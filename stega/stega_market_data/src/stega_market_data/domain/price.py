from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, ClassVar

from stega_core import Aggregate
from stega_contracts.market_data.command import PullKind

if TYPE_CHECKING:
    from datetime import datetime
    from decimal import Decimal


@dataclass(frozen=True, kw_only=True, slots=True)
class Price:
    ticker: str
    dt: datetime
    amount: Decimal


class PullStatus(Enum):
    REQUESTED = "requested"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True, kw_only=True)
class SymbolResult:
    ticker: str
    prices: list[Price] = field(default_factory=list)


class PricePull(Aggregate):
    __id_attr__: ClassVar[str] = "pull_id"

    def __init__(
        self,
        pull_id: str,
        kind: PullKind,
        status: PullStatus = PullStatus.REQUESTED,
        prices: list[Price] | None = None,
        version_number: int = 0,
    ) -> None:
        super().__init__(version_number)
        self.pull_id = pull_id
        self.kind = kind
        self.status = status
        self.prices = prices if prices is not None else []

    def init_transients(self) -> None:
        super().init_transients()
        self.prices = []

    @classmethod
    def open(cls, pull_id: str, kind: PullKind) -> PricePull:
        return cls(pull_id=pull_id, kind=kind, status=PullStatus.REQUESTED)

    def record_result(self, result: SymbolResult) -> None:
        self.prices.extend(result.prices)
