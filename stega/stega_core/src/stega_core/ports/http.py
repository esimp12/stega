import typing_extensions as T
from stega_lib import http

from stega_core.domain.portfolio import Portfolio

PORTFOLIO_BASE_URL = "http://localhost:8001/api"
PORTFOLIO_RETRIEVE_URL = f"{PORTFOLIO_BASE_URL}/portfolios"


class HttpRestPortfolioRepository:
    """Implementation of PortfolioRepository using HTTP REST API."""

    def add_portfolio(self, portfolio: Portfolio) -> None:
        """Add a portfolio to the repository.

        Args:
            portfolio (Portfolio): The portfolio to add.

        """
        # Implementation for adding a portfolio using HTTP POST request

    def get_portfolio(self, name: str) -> Portfolio:
        """Get a portfolio by name.

        Args:
            name (str): The name of the portfolio.

        Returns:
            Portfolio: The portfolio with the specified name.

        """
        with http.acquire_session(PORTFOLIO_BASE_URL, params={"name": name}) as session:
            resp = http.fetch(session, PORTFOLIO_RETRIEVE_URL)
            resp.raise_for_status()
            data = resp.json()
            return _extract_from_json(data)


def _extract_from_json(data: T.Mapping[str, T.Any]) -> Portfolio:
    return Portfolio(
        name=data["name"],
        assets={asset["symbol"]: asset["weight"] for asset in data["assets"]},
    )
