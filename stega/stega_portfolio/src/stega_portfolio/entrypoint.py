import asyncio
import logging

from hypercorn.asyncio import serve
from hypercorn.config import Config as HypercornConfig
from hypercorn.logging import Logger as HypercornLogger

from stega_portfolio.adapters.rest.app import create_app
from stega_portfolio.config import PortfolioConfig, create_config, create_logger


class CustomLogger(HypercornLogger):
    def __init__(self, hc_config: HypercornConfig) -> None:
        hc_config.access_log_format = "%(h)s %(r)s %(s)s %(b)s %(D)s"
        hc_config.accesslog = "-"
        super().__init__(hc_config)

        config = create_config()
        null_handler = logging.NullHandler() 
        log_level = config.STEGA_PORTFOLIO_LOG_LEVEL.upper()
        for logger in (self.error_logger, self.access_logger):
            if logger:
                logger.handlers.clear()
                logger.addHandler(null_handler)
                logger.setLevel(log_level)
                logger.propagate = True


def create_hypercorn_config(config: PortfolioConfig) -> HypercornConfig:
    hc_config = HypercornConfig()
    hc_config.bind = [
        f"{config.STEGA_PORTFOLIO_SERVER_ADDRESS}:{config.STEGA_PORTFOLIO_SERVER_PORT}",
    ]
    hc_config.logger_class = CustomLogger
    return hc_config


def run() -> None:
    config = create_config()
    logger = create_logger(config, third_party_loggers=["hypercorn"])
    logger.info("Starting stega portfolio service...")
    envvars_str = "\n  ".join(f"{k} => {v!r}" for k, v in config.get_envvars())
    envvars_str = "\n  " + envvars_str
    logger.debug("Using following configuration... %s", envvars_str)
    app = create_app(config)

    # run with hypercorn
    hc_config = create_hypercorn_config(config)
    asyncio.run(serve(app, hc_config))
