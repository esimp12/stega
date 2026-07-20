import os

from stega_config import BaseConfig, source
from stega_core import (
    RepositoryConfig,
    RepositoryRuntime,
    ServiceBrokerConfig,
    ServiceConfig,
)


class MarketDataConfig(
    ServiceConfig,
    ServiceBrokerConfig,
    RepositoryConfig,
    BaseConfig,
):
    __prefix__ = "STEGA_MARKET_DATA"

    DATA_DIR: str = source("env", default="~/.local/share/stega/market_data")

    REPOSITORY_DBNAME: str = source(
        "env",
        default="stega_market_data",
    )
    REPOSITORY_DBHOST: str = source(
        "env",
        default="market_data_db",
        depends_on="REPOSITORY_RUNTIME",
        depends_value=RepositoryRuntime.POSTGRES,
    )

    EOD_API_KEY: str = source("env")
    EOD_BASE_URL: str = source("env", default="https://eodhd.com/api")
    EOD_QUOTA_PER_MIN: int = source("env", default=1_000)
    EOD_QUOTA_PER_DAY: int = source("env", default=100_000)


class ProdConfig(MarketDataConfig):
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


class DevConfig(MarketDataConfig):
    LOG_LEVEL: str = source("env", default="DEBUG")


def create_config(env: str | None = None) -> MarketDataConfig:
    if env is None:
        env = os.getenv(f"{MarketDataConfig.__prefix__}_ENV", "dev").lower()
    return MarketDataConfig.create_config(env)
