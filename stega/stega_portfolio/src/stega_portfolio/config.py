import os

from stega_config import BaseConfig, source
from stega_core import (
    ReaderConfig,
    ReaderRuntime,
    RepositoryConfig,
    RepositoryRuntime,
    ServiceBrokerConfig,
    ServiceConfig,
)


class PortfolioConfig(
    ServiceConfig,
    ServiceBrokerConfig,
    RepositoryConfig,
    ReaderConfig,
    BaseConfig,
):
    __prefix__ = "STEGA_PORTFOLIO"

    DATA_DIR: str = source("env", default="~/.local/share/stega/portfolio")

    REPOSITORY_DBNAME: str = source(
        "env",
        default="stega_portfolio",
        depends_on="REPOSITORY_RUNTIME",
        depends_value=RepositoryRuntime.POSTGRES,
    )
    REPOSITORY_DBHOST: str = source(
        "env",
        default="portfolio_db",
        depends_on="REPOSITORY_RUNTIME",
        depends_value=RepositoryRuntime.POSTGRES,
    )
    READER_DBNAME: str = source(
        "env",
        default="stega_portfolio",
        depends_on="READER_RUNTIME",
        depends_value=ReaderRuntime.POSTGRES,
    )
    READER_DBHOST: str = source(
        "env",
        default="portfolio_db",
        depends_on="READER_RUNTIME",
        depends_value=ReaderRuntime.POSTGRES,
    )


class ProdConfig(PortfolioConfig):
    HOST: str = source("env", default="0.0.0.0")

    REPOSITORY_DBNAME: str = source(
        "file",
        path="/run/secrets",
        depends_on="REPOSITORY_RUNTIME",
        depends_value=RepositoryRuntime.POSTGRES,
    )
    REPOSITORY_DBHOST: str = source(
        "file",
        path="/run/secrets",
        depends_on="REPOSITORY_RUNTIME",
        depends_value=RepositoryRuntime.POSTGRES,
    )
    READER_DBNAME: str = source(
        "file",
        path="/run/secrets",
        depends_on="READER_RUNTIME",
        depends_value=ReaderRuntime.POSTGRES,
    )
    READER_DBHOST: str = source(
        "file",
        path="/run/secrets",
        depends_on="READER_RUNTIME",
        depends_value=ReaderRuntime.POSTGRES,
    )


class DevConfig(PortfolioConfig):
    LOG_LEVEL: str = source("env", default="DEBUG")


def create_config(env: str | None = None) -> PortfolioConfig:
    if env is None:
        env = os.getenv(f"{PortfolioConfig.__prefix__}_ENV", "dev").lower()
    return PortfolioConfig.create_config(env)
