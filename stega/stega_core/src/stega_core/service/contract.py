from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stega_core.service.port import StegaServicePort
    from stega_core.service.spec import ServiceSpec


@dataclass(frozen=True)
class ServiceContract:
    port_base: type[StegaServicePort]
    runtime_field: str
    specs: list[ServiceSpec]
