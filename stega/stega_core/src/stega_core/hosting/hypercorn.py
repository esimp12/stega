import logging
from collections.abc import Callable
from dataclasses import dataclass

from hypercorn.asyncio import serve
from hypercorn.config import Config as HypercornConfig
from hypercorn.logging import Logger as HypercornLogger
from quart import Quart
from stega_config import BaseConfig


@dataclass(frozen=True, kw_only=True)
class HypercornRuntimeFields:
    log_level_field: str
    server_address_field: str
    server_port_field: str


async def serve_hypercorn(
    app_factory: Callable[[BaseConfig], Quart],
    config: BaseConfig,
    runtime_fields: HypercornRuntimeFields,
) -> None:
    log_level = getattr(config, runtime_fields.log_level_field)

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
    address = getattr(config, runtime_fields.server_address_field)
    port = getattr(config, runtime_fields.server_port_field)
    hc_config = HypercornConfig()
    hc_config.bind = [f"{address}:{port}"]
    hc_config.logger_class = CustomLogger

    # create and serve app
    app = app_factory(config)
    await serve(app, hc_config)
