"""Public config entrypoint for stega."""

import typing_extensions as T

from config.base import BaseConfig, BasePortfolioConfig, ConfigType, create_config

CONFIG = T.cast(BaseConfig, create_config())
PORTFOLIO_CONFIG = T.cast(
    BasePortfolioConfig, create_config(config_type=ConfigType.PORTFOLIO)
)
