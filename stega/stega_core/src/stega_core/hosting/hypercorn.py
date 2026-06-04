import logging

from hypercorn.asyncio import serve
from hypercorn.config import Config as HypercornConfig
from hypercorn.logging import Logger as HypercornLogger
from quart import Quart


async def serve_hypercorn(
    app: Quart,
    log_level: int = logging.INFO,
    host: str = "127.0.0.1",
    port: int = 5000,
) -> None:
    # override hypercorn logging to stay consistent with app logging
    class CustomLogger(HypercornLogger):
        def __init__(self, hc_config: HypercornConfig) -> None:
            hc_config.access_log_format = "%(h)s %(r)s %(s)s %(b)s %(D)s"
            hc_config.accesslog = "-"
            super().__init__(hc_config)

            null_handler = logging.NullHandler()
            for logger in (self.access_logger, self.error_logger):
                if logger:
                    logger.handlers.clear()
                    logger.addHandler(null_handler)
                    logger.setLevel(log_level)
                    logger.propagate = True

    # create hypercorn config for serving
    hc_config = HypercornConfig()
    hc_config.bind = [f"{host}:{port}"]
    hc_config.logger_class = CustomLogger

    # create and serve app
    await serve(app, hc_config)
