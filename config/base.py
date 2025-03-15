"""Module for base config definitions."""

from __future__ import annotations

import os
import typing as T

from config.frozen import FrozenConfig, FrozenConfigMeta


def create_config(env: T.Optional[str] = None) -> BaseConfig:
    """Creates a new config instance.

    Args:
        env: A string of the environment name to load.

    Returns:
        A BaseConfig instance.
    """
    return BaseConfig.create_config(env)


def source_config_value(
    name: str,
    default: T.Optional[T.Any] = None,
    required: bool = False,
) -> T.Optional[T.Any]:
    """Load a config value from an environment variable.

    Args:
        name: A string of the environment variable name to source.
        default: A default value to return if the given environment variable does not
            exist.
        required: A bool indicating if the environment variable is required.

    Returns:
        The value corresponding to the given environment variable.
    """
    if name in os.environ:
        return os.environ[name]
    if required:
        raise ValueError(f"'{name}' is a required environment variable")
    return default


class BaseConfig(FrozenConfig):
    """See FrozenConfig.

    Attributes:
        __CONFIGS: A dict of config names to config classes.
    """

    # pylint: disable=too-few-public-methods

    __CONFIGS: T.Dict[str, FrozenConfigMeta] = {}

    STEGA_ENV: str

    STEGA_DBNAME: str = "stega"
    STEGA_DBUSER: str = source_config_value("STEGA_DBUSER", required=True)
    STEGA_DBPASSWORD: str = source_config_value("STEGA_DBPASSWORD", required=True)
    STEGA_DBHOST: str = "db"
    STEGA_DBPORT: int = 5432

    STEGA_EOD_API_TOKEN: str = source_config_value("STEGA_EOD_API_TOKEN", required=True)
    STEGA_EOD_API: str = "https://eodhistoricaldata.com/api"
    STEGA_EOD_API_MAX: int = 1000
    STEGA_EOD_API_PERIOD: int = 60
    STEGA_EOD_DATEFMT: str = "%Y-%m-%d"
    STEGA_EOD_EXCHANGE: str = "US"

    STEGA_SP500_URL: str = "https://en.wikipedia.org/wiki/List_of_S&P_500_companies"

    STEGA_TEST_SYMBOLS: T.List[str] = ["APPL", "MCD", "MSFT", "AMZN", "TSLA"]

    def __init_subclass__(cls, *args, **kwargs):
        """Registers subclass config.

        Args:
            *args: Args to supply to config subclass initialization.
            **kwargs: Kwargs to supply to config subclass initialization.

        Returns:
            A BaseConfig subclass.
        """
        cls.__CONFIGS[cls.__name__] = cls
        return super().__init_subclass__(*args, **kwargs)

    @classmethod
    def create_config(cls, env: T.Optional[str] = None) -> BaseConfig:
        """Creates a config from a environment name key.

        Args:
            env: A string of the name of the config environment to load. If None, then
                a 'base' config is created.

        Returns:
            A BaseConfig instance.
        """
        if env is None:
            env = os.getenv("STEGA", "base")
        env = env.title()
        config = cls.__CONFIGS.get(f"{env}Config", BaseConfig)
        if config is None:
            raise ValueError(f"{env} not a valid config")
        return config()  # type: ignore
