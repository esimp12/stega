import os
from pathlib import Path

from stega_config import BaseConfig, source
from stega_contracts.edge import EdgeServiceConfig

from stega_cli.ports.client import ClientConfig


class CliConfig(ClientConfig, EdgeServiceConfig, BaseConfig):
    __prefix__ = "STEGA_CLI"

    PROFILE: str = source("env", default="local")
    LOG_LEVEL: str = source("env", default="INFO")

    DATA_DIR: str = source("env", default="~/.local/share/stega/cli")
    CACHE_DIR: str = source("env", default="~/.cache/stega/cli")
    STATE_DIR: str = source("env", default="~/.local/share/stega/cli")

    SOCKET_FILE: str = source("env", default="stega.sock")
    DB_FILE: str = source("env", default="stega.db")

    @property
    def data_dir(self) -> Path:
        return _ensure(Path(self.DATA_DIR).expanduser() / self.PROFILE)

    @property
    def state_dir(self) -> Path:
        return _ensure(Path(self.STATE_DIR).expanduser() / self.PROFILE)

    @property
    def socket_path(self) -> str:
        return str(self.state_dir / self.SOCKET_FILE)

    @property
    def db_path(self) -> str:
        return str(self.data_dir / self.DB_FILE)


class ProdConfig(CliConfig): ...


class DevConfig(CliConfig):
    LOG_LEVEL: str = source("env", default="DEBUG")


def create_config(env: str | None = None) -> CliConfig:
    if env is None:
        env = os.getenv(f"{CliConfig.__prefix__}_ENV", "dev").lower()
    return CliConfig.create_config(env)


def _ensure(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
