from abc import abstractmethod

from stega_contracts.portfolio.view import PortfolioListView, PortfolioView
from stega_core import AbstractReader


class PortfolioReader(AbstractReader):
    @abstractmethod
    async def get(self, portfolio_id: str) -> PortfolioView | None:
        pass

    @abstractmethod
    async def list(self) -> PortfolioListView:
        pass
