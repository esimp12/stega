from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from stega_core.service.http import HttpChannel, HttpTransport
from stega_core.service.memory import InMemoryChannel, InMemoryTransport

if TYPE_CHECKING:
    from collections.abc import Callable

    from stega_config import BaseConfig

    from stega_core.bootstrap import RuntimeFlag
    from stega_core.bus import MessageBus
    from stega_core.hosting import Route
    from stega_core.service.channel import Channel
    from stega_core.service.transport import AbstractTransport


@dataclass(frozen=True, kw_only=True)
class ServiceSpec(ABC):
    runtime: RuntimeFlag

    @abstractmethod
    def channel_factory(self, config: BaseConfig) -> Callable[[], Channel]: ...

    @property
    @abstractmethod
    def transport_type(self) -> type[AbstractTransport]: ...


@dataclass(frozen=True, kw_only=True)
class HttpServiceSpec(ServiceSpec):
    runtime: RuntimeFlag
    base_url_field: str
    routes: list[Route]

    def channel_factory(self, config: BaseConfig) -> Callable[[], Channel]:
        base_url = getattr(config, self.base_url_field)
        routes = {r.msg_type: r for r in self.routes}
        return lambda: HttpChannel(base_url, routes)

    @property
    def transport_type(self) -> type[AbstractTransport]:
        return HttpTransport


@dataclass(frozen=True, kw_only=True)
class InMemoryServiceSpec(ServiceSpec):
    runtime: RuntimeFlag
    bus: MessageBus

    def channel_factory(self, _: BaseConfig) -> Callable[[], Channel]:
        bus = self.bus
        return lambda: InMemoryChannel(bus)

    @property
    def transport_type(self) -> type[AbstractTransport]:
        return InMemoryTransport
