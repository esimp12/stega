from abc import ABC, abstractmethod

from stega_edge.config import create_config, create_logger
from stega_edge.domain.portfolio import PortfolioData


class PortfolioServicePort(ABC):

    def __init__(self) -> None:
        self.config = create_config()
        self.logger = create_logger(self.config)

    @abstractmethod
    async def get(self, portfolio_id: str) -> PortfolioData:
        ...

    @abstractmethod
    async def list(self) -> list[PortfolioData]:
        ...

    @abstractmethod
    async def create(self, correlation_id: str, portfolio_data: PortfolioData) -> None:
        ...

    @abstractmethod
    async def update(self, correlation_id: str, portfolio_id: str, portfolio_data: PortfolioData) -> None:
        ...

    @abstractmethod
    async def delete(self, correlation_id: str, portfolio_id: str) -> None:
        ...
