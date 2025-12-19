"""HTTP REST implementation of the PortfolioServicePort interface."""

from stega_lib import http

from stega_core.domain.portfolio import PortfolioData
from stega_core.ports.base import PortfolioServicePort


class HttpRestPortfolioServicePort(PortfolioServicePort):
    """Implementation of PortfolioServicePort using HTTP REST API."""

    def create(
        self,
        correlation_id: str,
        portfolio: PortfolioData,
    ) -> str:
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
                headers={
                    "X-Request-Id": correlation_id,
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
            return PortfolioData(name=data["name"], assets=data["assets"])

    def update(self, correlation_id: str, id: str, portfolio: PortfolioData) -> None:
        return None

    def delete(self, correlation_id: str, id: str) -> None:
        return None

    def list(self) -> list[PortfolioData]:
        """Get all existing portfolios.

        Returns:
            list[PortfolioData]: A list of existing portfolios.

        """
        with http.acquire_session(self.config.portfolio_service_url) as session:
            resp = session.get("/portfolios")
            resp.raise_for_status()
            data = resp.json()
            return [
                PortfolioData(name=view["name"], assets=view["assets"])
                for view in data["view"]
            ]
