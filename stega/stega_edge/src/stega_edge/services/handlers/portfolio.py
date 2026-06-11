
from stega_contracts.portfolio.command import CreatePortfolio, DeletePortfolio, UpdatePortfolio
from stega_contracts.portfolio.query import GetPortfolio, ListPortfolios
from stega_contracts.portfolio.port import PortfolioServicePort
from stega_contracts.portfolio.view import PortfolioView, PortfolioListView


async def get_portfolio(query: GetPortfolio, service: PortfolioServicePort) -> PortfolioView:
    async with service:
        await service.forward(query)


async def list_portfolios(query: ListPortfolios, service: PortfolioServicePort) -> PortfolioListView:
    async with service:
        await service.forward(query)


async def create_portfolio(cmd: CreatePortfolio, service: PortfolioServicePort) -> None:
    async with service:
        await service.forward(cmd)


async def update_portfolio(cmd: UpdatePortfolio, service: PortfolioServicePort) -> None: 
    async with service:
        await service.forward(cmd)


async def delete_portfolio(cmd: DeletePortfolio, service: PortfolioServicePort) -> None:
    async with service:
        await service.forward(cmd)
