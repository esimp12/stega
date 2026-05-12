"""HTTP REST implementation of the PortfolioServicePort interface."""

from stega_lib import http

from stega_core.domain.errors import CoreAppError
from stega_core.domain.portfolio import PortfolioData
from stega_core.ports.base import PortfolioServicePort


class HttpRestPortfolioServicePort(PortfolioServicePort):
    """Implementation of PortfolioServicePort using HTTP REST API."""

    def get(self, portfolio_id: str) -> PortfolioData:
        """See PortfolioServicePort."""
        url = f"portfolio/{portfolio_id}"
        with http.acquire_session(self.config.portfolio_service_url) as session:
            resp = session.get(url)
            data = resp.json()
            if not data["ok"]:
                raise CoreAppError(data["msg"])
            view = data["view"]
            return PortfolioData(name=view["name"], assets=view["assets"])

    def list(self) -> list[PortfolioData]:
        """See PortfolioServicePort."""
        url = "portfolios"
        with http.acquire_session(self.config.portfolio_service_url) as session:
            resp = session.get(url)
            data = resp.json()
            if not data["ok"]:
                raise CoreAppError(data["msg"])
            return [
                PortfolioData(portfolio_id=view["portfolio_id"], name=view["name"], assets=view["assets"])
                for view in data["view"]
            ]

    def create(self, correlation_id: str, portfolio_data: PortfolioData) -> str:
        """See PortfolioServicePort."""
        url = "portfolios"
        headers = {"X-Request-Id": correlation_id}
        body = {
            "name": portfolio_data.name,
            "assets": {asset.symbol: asset.weight for asset in portfolio_data.assets},
        }
        with http.acquire_session(self.config.portfolio_service_url) as session:
            resp = session.post(url, headers=headers, json=body)
            data = resp.json()
            if not data["ok"]:
                raise CoreAppError(data["msg"])
            return data["id"]

    def update(self, correlation_id: str, portfolio_id: str, portfolio_data: PortfolioData) -> None:
        """See PortfolioServicePort."""
        raise NotImplementedError

    def delete(self, correlation_id: str, portfolio_id: str) -> None:
        """See PortfolioServicePort."""
        raise NotImplementedError
