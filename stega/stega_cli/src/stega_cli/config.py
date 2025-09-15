"""Configuration module for the stega CLI."""

import inspect
import logging
import os

from stega_config import BaseConfig


class CliConfig(BaseConfig):
    """Base configuration for the stega CLI.

    NOTE: This class is intended to be extended by specific environment configurations.
    """

    STEGA_CLI_ENV: str
    STEGA_CLI_DEBUG: bool = False

    STEGA_CLI_LOG_LEVEL: str = "INFO"

    STEGA_CORE_SERVER_NAME: str = "localhost"
    STEGA_CORE_SERVER_PORT: int = 20000

    @property
    def core_service_url(self) -> str:
        """Get the core service API url."""
        return (
            f"http://{self.STEGA_CORE_SERVER_NAME}:{self.STEGA_CORE_SERVER_PORT}/api"
        )


class ProdConfig(CliConfig):
    """Production configuration for the stega CLI."""

    STEGA_CLI_ENV: str = "prod"


class DevConfig(CliConfig):
    """Development configuration for the stega CLI."""

    STEGA_CLI_ENV: str = "dev"
    STEGA_CLI_DEBUG: bool = True

    STEGA_CLI_LOG_LEVEL: str = "DEBUG"


def create_config(env: str | None = None) -> CliConfig:
    """Create a CLI service configuration instance based on the environment.

    Args:
        env: The environment for which to create the configuration. If None,
            defaults to 'dev'.

    Returns:
        An instance of CliConfig for the specified environment.

    """
    if env is None:
        env = os.getenv("STEGA_CLI_ENV", "dev").lower()
    return CliConfig.create_config(env)


def create_logger(
    config: CliConfig,
    third_party_loggers: list[str] | None = None,
) -> logging.Logger:
    """Create a logger for the core service.

    Args:
        config: The configuration instance for the core service.
        third_party_loggers: Optional list of third-party loggers to configure.

    Returns:
        A logger instance configured for the calling module of the core service.

    """
    if third_party_loggers is None:
        third_party_loggers = []

    # Setup stream handler for the loggers
    log_level = config.STEGA_CLI_LOG_LEVEL.upper()
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
