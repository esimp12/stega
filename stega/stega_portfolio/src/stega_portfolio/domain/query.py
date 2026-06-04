from dataclasses import dataclass

from stega_core import Query

from stega_portfolio.domain.view import PortfolioView, PortfolioListView


@dataclass(frozen=True, kw_only=True)
class GetPortfolio(Query[PortfolioView]):
    portfolio_id: str


@dataclass(frozen=True, kw_only=True)
class ListPortfolios(Query[PortfolioListView]):
    pass
