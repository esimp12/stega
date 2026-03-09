"""Application views for handling read only requests to portfolios."""


from stega_portfolio.views.views import PortfolioView
from stega_portfolio.services.uow.base import AbstractUnitOfWork


def get_portfolio(uow: AbstractUnitOfWork, portfolio_id: str) -> PortfolioView | None:
    """Get a single portfolio view."""
    with uow:
        portfolio = uow.portfolios.get(portfolio_id)
        if portfolio is None:
            return None
        return PortfolioView.from_portfolio(portfolio)


def list_portfolios(uow: AbstractUnitOfWork) -> list[PortfolioView]:
    """Get a list of all portfolio views."""
    with uow:
        portfolios = uow.portfolios.list()
        return [
            PortfolioView.from_portfolio(portfolio)
            for portfolio in portfolios
        ]

