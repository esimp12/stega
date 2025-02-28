"""Module for common config definitions."""

from config.base import BaseConfig


class ProdConfig(BaseConfig):
    """See BaseConfig."""

    # pylint: disable=too-few-public-methods

    STEGA_ENV: str = "prod"


class StagingConfig(BaseConfig):
    """See BaseConfig."""

    # pylint: disable=too-few-public-methods

    STEGA_ENV: str = "staging"


class DevConfig(BaseConfig):
    """See BaseConfig."""

    # pylint: disable=too-few-public-methods

    STEGA_ENV: str = "dev"


class TestConfig(BaseConfig):
    """See BaseConfig."""

    # pylint: disable=too-few-public-methods

    STEGA_ENV: str = "test"
