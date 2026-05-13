import inspect
import logging
import os

from stega_config import BaseConfig, source


class EdgeConfig(BaseConfig):
    STEGA_EDGE_ENV: str
    STEGA_EDGE_DEBUG: bool = False
    STEGA_EDGE_HYPERCORN: bool = False

    STEGA_EDGE_LOG_LEVEL: str = "INFO"

    STEGA_EDGE_HYPERCORN_WORKERS: int = 4
    STEGA_EDGE_SERVER_ADDRESS: str = "0.0.0.0"
    STEGA_EDGE_SERVER_PORT: int = 5000

    STEGA_PORTFOLIO_SERVER_NAME: str = "portfolio"
    STEGA_PORTFOLIO_SERVER_PORT: int = 5000

    STEGA_BROKER_EXCHANGE_NAME: str = "events"
    STEGA_BROKER_USERNAME: str
    STEGA_BROKER_PASSWORD: str
    STEGA_BROKER_HOST: str = "broker"
    STEGA_BROKER_PORT: int = 5672

    @property
    def portfolio_service_url(self) -> str:
        return f"http://{self.STEGA_PORTFOLIO_SERVER_NAME}:{self.STEGA_PORTFOLIO_SERVER_PORT}/api"


class ProdConfig(EdgeConfig):
    STEGA_EDGE_ENV: str = "prod"
    STEGA_EDGE_HYPERCORN: bool = True

    STEGA_BROKER_USERNAME: str = source("env")
    STEGA_BROKER_PASSWORD: str = source("env")


class DevConfig(EdgeConfig):
    STEGA_EDGE_ENV: str = "dev"
    STEGA_EDGE_DEBUG: bool = True

    STEGA_EDGE_LOG_LEVEL: str = "DEBUG"

    STEGA_EDGE_SERVER_ADDRESS: str = "0.0.0.0"

    STEGA_BROKER_USERNAME: str = source("env")
    STEGA_BROKER_PASSWORD: str = source("env")


def create_config(env: str | None = None) -> EdgeConfig:
    if env is None:
        env = os.getenv("STEGA_EDGE_ENV", "dev").lower()
    return EdgeConfig.create_config(env)


def create_logger(
    config: EdgeConfig,
    third_party_loggers: list[str] | None = None,
) -> logging.Logger:
    if third_party_loggers is None:
        third_party_loggers = []

    # Setup stream handler for the loggers
    log_level = config.STEGA_EDGE_LOG_LEVEL.upper()
    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    # Configure the root logger
    project_name = f"{__name__.split('.')[0]}"
    root_logger = logging.getLogger(project_name)
    if not root_logger.hasHandlers():
        root_logger.setLevel(log_level)
        root_logger.addHandler(handler)

    # Configure third-party loggers
    for third_party_logger_name in third_party_loggers:
        third_party_logger = logging.getLogger(third_party_logger_name)
        # Clear any existing handlers so that we can set our own
        if handler not in third_party_logger.handlers:
            third_party_logger.handlers.clear()

        # Set the log level and add the handler if it doesn't already exist
        if not third_party_logger.hasHandlers():
            third_party_logger.setLevel(log_level)
            third_party_logger.addHandler(handler)

    # Return the logger for the calling module
    calling_module = get_caller_module()
    return logging.getLogger(calling_module)


def get_caller_module() -> str:
    frame = inspect.currentframe()
    caller_frame = frame.f_back
    module = inspect.getmodule(caller_frame)
    return module.__name__
