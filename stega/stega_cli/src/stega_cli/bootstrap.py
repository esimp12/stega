from __future__ import annotations

from typing import TYPE_CHECKING

from stega_contracts.edge import CONTRACT as EDGE_CONTRACT

from stega_cli.config import create_config
from stega_cli.ports.client import CONTRACT as CLIENT_CONTRACT

if TYPE_CHECKING:
    from stega_config import BaseConfig
    from stega_core import ServiceContract, ServiceSpec, StegaServicePort

    from stega_cli.config import CliConfig


def build_port(contract: ServiceContract, config: BaseConfig) -> StegaServicePort:
    spec = _select(contract, config)
    return contract.port_base(spec.channel_factory(config), spec.transport_type)


def build_client_port(config: CliConfig | None = None) -> StegaServicePort:
    if config is None:
        config = create_config()
    return build_port(CLIENT_CONTRACT, config)


def build_edge_port(config: CliConfig | None = None) -> StegaServicePort:
    if config is None:
        config = create_config()
    return build_port(EDGE_CONTRACT, config)


def _select(contract: ServiceContract, config: BaseConfig) -> ServiceSpec:
    runtime = getattr(config, contract.runtime_field)
    for spec in contract.specs:
        if spec.runtime is runtime:
            return spec
    err_msg = f"No spec registered for {contract.runtime_field}={runtime}"
    raise RuntimeError(err_msg)
