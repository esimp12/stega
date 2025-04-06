from __future__ import annotations

import typing_extensions as T

from config.base import BasePortfolioConfig, ConfigType, create_config
from src.portfolio.domain import Portfolio
from src.portfolio.ports.registry import (
    PORTFOLIO_REPO_REGISTRY,
    PortfolioRepositoryType,
)


class PortfolioRepository(T.Protocol):
    """Abstract base class for portfolio repositories."""

    def add_portfolio(self, portfolio: Portfolio) -> None:
        """Add a portfolio to the repository.

        Args:
            portfolio (Portfolio): The portfolio to add.
        """
        raise NotImplementedError

    def get_portfolio(self, name: str) -> Portfolio:
        """Get a portfolio by name.

        Args:
            name (str): The name of the portfolio.

        Returns:
            Portfolio: The portfolio with the specified name.
        """
        raise NotImplementedError

    @classmethod
    def create_repo(
        cls,
        repo_type_str: str,
        config: T.Optional[BasePortfolioConfig] = None,
    ) -> PortfolioRepository:
        """Create a portfolio repository of the specified type.

        Args:
            repo_type_str (str): The type of portfolio repository to create.

        Returns:
            PortfolioRepository: An instance of the specified portfolio repository.
        """
        if config is None:
            config = T.cast(
                BasePortfolioConfig, create_config(config_type=ConfigType.PORTFOLIO)
            )
        repo_type = PortfolioRepositoryType.from_str(repo_type_str)
        if repo_type not in PORTFOLIO_REPO_REGISTRY:
            raise ValueError(f"Unsupported portfolio repository type: {repo_type}")
        repo_class = PORTFOLIO_REPO_REGISTRY[repo_type]
        repo_kwargs = PORTFOLIO_REPO_REGISTRY[repo_type](config)
        return repo_class(**repo_kwargs)
