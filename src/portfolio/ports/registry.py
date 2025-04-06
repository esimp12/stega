from __future__ import annotations

from enum import Enum

import typing_extensions as T

from config.base import BasePortfolioConfig
from src.db import DbConnArgs
from src.portfolio.ports.db import PostgreSqlPortfolioRepository


class PortfolioRepositoryType(Enum):
    """Enum for portfolio repository types."""

    POSTGRESQL = "postgresql"

    @classmethod
    def from_str(cls, repo_type_str: str) -> PortfolioRepositoryType:
        """Get the portfolio repository type from the string.

        Args:
            repo_type_str (str): The string representation of the portfolio
                repository type.

        Returns:
            PortfolioRepositoryType: The corresponding portfolio repository type.

        Raises:
            ValueError: If the string does not match any known portfolio repository
                type.
        """
        try:
            return cls[repo_type_str.upper()]
        except KeyError:
            raise ValueError(f"Unsupported portfolio repository type: {repo_type_str}")


def _create_postgresql_kwargs(config: BasePortfolioConfig) -> T.Dict[str, T.Any]:
    return {
        "dbargs": DbConnArgs(
            dbname=config.STEGA_PORTFOLIO_DB_NAME,
            username=config.STEGA_PORTFOLIO_DB_USER,
            password=config.STEGA_PORTFOLIO_DB_PASSWORD,
            host=config.STEGA_PORTFOLIO_DB_HOST,
            port=config.STEGA_PORTFOLIO_DB_PORT,
        )
    }


PORTFOLIO_REPO_REGISTRY: T.Mapping[PortfolioRepositoryType, T.Type] = {
    PortfolioRepositoryType.POSTGRESQL: PostgreSqlPortfolioRepository,
}


PORTFOLIO_REPO_KWARGS_REGISTRY: T.Mapping[PortfolioRepositoryType, T.Callable] = {
    PortfolioRepositoryType.POSTGRESQL: _create_postgresql_kwargs,
}
