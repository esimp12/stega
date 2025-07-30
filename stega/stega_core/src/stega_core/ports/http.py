"""HTTP REST implementation of the PortfolioServicePort interface."""

from stega_lib import http

from stega_core.domain.portfolio import PortfolioData
from stega_core.ports.base import PortfolioServicePort


class HttpRestPortfolioServicePort(PortfolioServicePort):
    """Implementation of PortfolioServicePort using HTTP REST API."""

    def create(self, portfolio: PortfolioData) -> str:
        """Create a new portfolio.

        Args:
            portfolio (PortfolioData): The portfolio data to create.

        Returns:
            str: The ID of the created portfolio.

        """
        with http.acquire_session(self.config.portfolio_service_url) as session:
            resp = session.post(
                "portfolios",
                json={
                    "name": portfolio.name,
                    "assets": {asset.symbol: asset.weight for asset in portfolio.assets},
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["id"]

    def get(self, id: str) -> PortfolioData:
        """Get a portfolio by its unique ID.

        Args:
            id (str): The unique ID of the portfolio.

        Returns:
            PortfolioData: The portfolio with the specified ID.

        """
        with http.acquire_session(self.config.portfolio_service_url) as session:
            resp = session.get(f"portfolios/{id}")
            resp.raise_for_status()
            data = resp.json()
            return PortfolioData(id=data["id"], name=data["name"], assets=data["assets"])

    def update(self, id: str, portfolio: PortfolioData) -> None:
        return None

    def delete(self, id: str) -> None:
        return None
