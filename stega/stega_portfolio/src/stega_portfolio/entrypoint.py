import asyncio

from hypercorn.asyncio import serve
from hypercorn.config import Config as HypercornConfig

from stega_portfolio.adapters.rest.app import create_app
from stega_portfolio.config import PortfolioConfig, create_config, create_logger


def create_hypercorn_config(config: PortfolioConfig) -> HypercornConfig:
    hc_config = HypercornConfig()
    hc_config.bind = [
        f"{config.STEGA_PORTFOLIO_SERVER_ADDRESS}:{config.STEGA_PORTFOLIO_SERVER_PORT}",
    ]
    hc_config.loglevel = config.STEGA_PORTFOLIO_LOG_LEVEL.lower()

    hc_config.errorlog = "hypercorn.error"
    hc_config.accesslog = "hypercorn.accesslog"
    return hc_config


def run() -> None:
    config = create_config()
    logger = create_logger(config, third_party_loggers=["hypercorn.error", "hypercorn.access"])
    logger.info("Starting stega portfolio service...")
    envvars_str = "\n  ".join(f"{k} => {v!r}" for k, v in config.get_envvars())
    envvars_str = "\n  " + envvars_str
    logger.debug("Using following configuration... %s", envvars_str)
    app = create_app(config)

    # run with hypercorn
    if config.STEGA_PORTFOLIO_HYPERCORN:
        hc_config = create_hypercorn_config(config)
        asyncio.run(serve(app, hc_config))
    # run with quart
    else:
        app.run(
            host=config.STEGA_PORTFOLIO_SERVER_ADDRESS,
            port=config.STEGA_PORTFOLIO_SERVER_PORT,
            debug=config.STEGA_PORTFOLIO_DEBUG,
        )
