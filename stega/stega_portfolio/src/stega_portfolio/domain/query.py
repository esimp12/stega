from dataclasses import dataclass

from stega_core import Query


@dataclass(frozen=True, kw_only=True)
class GetPortfolio(Query):
    portfolio_id: str


@dataclass(frozen=True, kw_only=True)
class ListPortfolios(Query):
    pass
