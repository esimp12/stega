"""Application views for handling read only requests to portfolios."""


from stega_portfolio.views.views import PortfolioView
from stega_portfolio.services.uow.base import AbstractUnitOfWork


def list_portfolios(uow: AbstractUnitOfWork) -> list[PortfolioView]:
    """Get a list of all portfolio views."""
    with uow:
        portfolios = uow.portfolios.list()
        return [
            PortfolioView.from_portfolio(portfolio)
            for portfolio in portfolios
        ]

