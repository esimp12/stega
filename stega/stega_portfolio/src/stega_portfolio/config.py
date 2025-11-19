"""Configuration module for the portfolio service."""

import inspect
import logging
import os
from pathlib import Path
from urllib.parse import quote_plus

from stega_config import BaseConfig, source


class PortfolioConfig(BaseConfig):
    """Base configuration for the portfolio service.

    NOTE: This class is intended to be extended by specific environment configurations.
    """

    STEGA_PORTFOLIO_ENV: str
    STEGA_PORTFOLIO_DEBUG: bool = False
    STEGA_PORTFOLIO_GUNICORN: bool = False

    STEGA_PORTFOLIO_CONFIG_DIR: str = ".portfolio"
    STEGA_PORTFOLIO_LOG_LEVEL: str = "INFO"

    STEGA_PORTFOLIO_GUNICORN_WORKERS: int = 4
    STEGA_PORTFOLIO_SERVER_ADDRESS: str = "0.0.0.0"
    STEGA_PORTFOLIO_SERVER_PORT: int = 5000

    STEGA_PORTFOLIO_DBNAME: str = "stega_portfolio"
    STEGA_PORTFOLIO_DBUSER: str
    STEGA_PORTFOLIO_DBPASSWORD: str
    STEGA_PORTFOLIO_DBHOST: str = "portfolio_db"
    STEGA_PORTFOLIO_DBPORT: int = 5432

    STEGA_BROKER_EXCHANGE: str = "events"
    STEGA_BROKER_USER: str
    STEGA_BROKER_PASS: str
    STEGA_BROKER_HOST: str = "broker"
    STEGA_BROKER_PORT: int = 5000

    @property
    def root(self) -> Path:
        """Root file path of the application.

        Returns:
            A Path object.

        """
        return Path(__file__).parent.parent.absolute()

    @property
    def path(self) -> Path:
        """Path to the application config directory.

        Returns:
            A Path object.

        """
        return self.root / self.STEGA_PORTFOLIO_CONFIG_DIR

    @property
    def db_uri(self) -> str:
        """Returns the database URI for the portfolio service."""
        raise NotImplementedError


class ProdConfig(PortfolioConfig):
    """Production configuration for the portfolio service."""

    STEGA_PORTFOLIO_ENV: str = "prod"
    STEGA_PORTFOLIO_GUNICORN: bool = True

    STEGA_PORTFOLIO_DBUSER: str = source("file", path="/run/secrets")
    STEGA_PORTFOLIO_DBPASSWORD: str = source("file", path="/run/secrets")

    @property
    def db_uri(self) -> str:
        """Returns the database URI for the portfolio service."""
        user = self.STEGA_PORTFOLIO_DBUSER
        password = quote_plus(self.STEGA_PORTFOLIO_DBPASSWORD)
        host = self.STEGA_PORTFOLIO_DBHOST
        port = self.STEGA_PORTFOLIO_DBPORT
        db_name = self.STEGA_PORTFOLIO_DBNAME
        return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


class DevConfig(PortfolioConfig):
    """Development configuration for the portfolio service."""

    STEGA_PORTFOLIO_ENV: str = "dev"
    STEGA_PORTFOLIO_DEBUG: bool = True

    STEGA_PORTFOLIO_LOG_LEVEL: str = "DEBUG"

    STEGA_PORTFOLIO_SERVER_ADDRESS: str = "127.0.0.1"

    STEGA_PORTFOLIO_DBUSER: str = source("env")
    STEGA_PORTFOLIO_DBPASSWORD: str = source("env")

    STEGA_BROKER_USER: str = source("env")
    STEGA_BROKER_PASS: str = source("env")

    @property
    def db_uri(self) -> str:
        """Returns the database URI for the portfolio service."""
        if not Path.exists(self.path):
            Path.mkdir(self.path)
        path = self.path / f"{self.STEGA_PORTFOLIO_DBNAME}.db"
        return f"sqlite:///{path}"


def create_config(env: str | None = None) -> PortfolioConfig:
    """Create a portfolio service configuration instance based on the environment.

    Args:
        env: The environment for which to create the configuration. If None,
            defaults to 'dev'.

    Returns:
        An instance of PorftolioConfig for the specified environment.

    """
    if env is None:
        env = os.getenv("STEGA_PORTFOLIO_ENV", "dev").lower()
    return PortfolioConfig.create_config(env)


def create_logger(
    config: PortfolioConfig,
    third_party_loggers: list[str] | None = None,
) -> logging.Logger:
    """Create a logger for the portfolio service.

    Args:
        config: The configuration instance for the portfolio service.
        third_party_loggers: Optional list of third-party loggers to configure.

    Returns:
        A logger instance configured for the calling module of the portfolio service.

    """
    if third_party_loggers is None:
        third_party_loggers = []

    # Setup stream handler for the loggers
    log_level = config.STEGA_PORTFOLIO_LOG_LEVEL.upper()
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
    """Get the name of the module that called this function."""
    frame = inspect.currentframe()
    caller_frame = frame.f_back
    module = inspect.getmodule(caller_frame)
    return module.__name__
