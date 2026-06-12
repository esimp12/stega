import os

from stega_config import BaseConfig, source
from stega_contracts.portfolio import PortfolioServiceConfig
from stega_core import (
    ClientBrokerConfig,
    ServiceBrokerConfig,
    ServiceConfig,
)


class EdgeConfig(
    ServiceConfig,
    ClientBrokerConfig,
    ServiceBrokerConfig,
    PortfolioServiceConfig,
    BaseConfig,
):
    __prefix__ = "STEGA_EDGE"


class ProdConfig(EdgeConfig):
    HOST: str = source("env", default="0.0.0.0")


class DevConfig(EdgeConfig):
    LOG_LEVEL: str = source("env", default="DEBUG")


def create_config(env: str | None = None) -> EdgeConfig:
    if env is None:
        env = os.getenv(f"{EdgeConfig.__prefix__}_ENV", "dev").lower()
    return EdgeConfig.create_config(env)
