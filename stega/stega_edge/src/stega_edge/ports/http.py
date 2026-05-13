from stega_utils import http
from stega_edge.domain.error import AppError
from stega_edge.domain.portfolio import PortfolioData
from stega_edge.ports.base import PortfolioServicePort


class HttpRestPortfolioServicePort(PortfolioServicePort):

    async def get(self, portfolio_id: str) -> PortfolioData:
        url = f"portfolio/{portfolio_id}"
        async with http.acquire_async_session(self.config.portfolio_service_url) as session:
            resp = session.get(url)
            data = resp.json()
            if not data["ok"]:
                raise AppError(data["msg"])
            view = data["view"]
            return PortfolioData(name=view["name"], assets=view["assets"])

    async def list(self) -> list[PortfolioData]:
        url = "portfolios"
        async with http.acquire_async_session(self.config.portfolio_service_url) as session:
            resp = session.get(url)
            data = resp.json()
            if not data["ok"]:
                raise AppError(data["msg"])
            return [
                PortfolioData(portfolio_id=view["portfolio_id"], name=view["name"], assets=view["assets"])
                for view in data["view"]
            ]

    async def create(self, correlation_id: str, portfolio_data: PortfolioData) -> None:
        url = "portfolios"
        headers = {"X-Request-Id": correlation_id}
        body = {
            "name": portfolio_data.name,
            "assets": {asset.symbol: asset.weight for asset in portfolio_data.assets},
        }
        async with http.acquire_async_session(self.config.portfolio_service_url) as session:
            resp = session.post(url, headers=headers, json=body)
            # TODO

    async def update(self, correlation_id: str, portfolio_id: str, portfolio_data: PortfolioData) -> None:
        pass

    async def delete(self, correlation_id: str, portfolio_id: str) -> None:
        pass
