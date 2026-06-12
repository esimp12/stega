from __future__ import annotations

from contextlib import asynccontextmanager
from enum import Flag, auto
from typing import TYPE_CHECKING, Any

from stega_core.broker import (
    ClientBroker,
    ServiceBroker,
    make_client_publish_handler,
    make_service_publish_handler,
)
from stega_core.bus import (
    MessageBus,
)
from stega_core.di import (
    Dependency,
    DependencyContainer,
    MessageHandler,
    Scope,
    bind_handler,
)
from stega_core.message import (
    Command,
    Event,
    Query,
)
from stega_core.query_context import (
    AbstractQueryContext,
)
from stega_core.registry import (
    CommandRegistry,
    EventRegistry,
    QueryRegistry,
    ReaderRegistry,
    RepositoryRegistry,
)
from stega_core.uow import (
    AbstractUnitOfWork,
)

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable, Iterator

    from stega_config import BaseConfig

    from stega_core.reader import (
        AbstractReader,
    )
    from stega_core.repository import (
        AbstractRepository,
    )
    from stega_core.service import (
        AbstractTransport,
        Channel,
        ServiceContract,
        ServiceSpec,
        StegaServicePort,
    )


class RuntimeFlag(Flag):
    @classmethod
    def _missing_(
        cls,
        value: Any,  # noqa: ANN401
    ) -> RuntimeFlag:
        if isinstance(value, str):
            try:
                return cls[value.strip().upper()]
            except KeyError:
                return None
        return super()._missing_(value)


class RepositoryRuntime(RuntimeFlag):
    MEMORY = auto()
    SQLITE = auto()
    POSTGRES = auto()


class ReaderRuntime(RuntimeFlag):
    MEMORY = auto()
    SQLITE = auto()
    POSTGRES = auto()


class ServiceBrokerRuntime(RuntimeFlag):
    MEMORY = auto()
    RABBITMQ = auto()


class ClientBrokerRuntime(RuntimeFlag):
    MEMORY = auto()
    RABBITMQ = auto()


class ServiceBuilder:
    def __init__(self, config: BaseConfig) -> None:
        self._config = config

        # shared runtimes
        self._repo_runtime_field: str | None = None
        self._reader_runtime_field: str | None = None
        self._service_broker_runtime_field: str | None = None
        self._client_broker_runtime_field: str | None = None

        # session factories
        self._uow_session_factories: dict[RepositoryRuntime, Callable[[BaseConfig], Any]] = {}
        self._qctx_session_factories: dict[ReaderRuntime, Callable[[BaseConfig], Any]] = {}

        # repo and reader based runtime registrations
        self._repo_classes: dict[
            type[AbstractRepository],
            dict[RepositoryRuntime, type[AbstractRepository]],
        ] = {}
        self._reader_classes: dict[
            type[AbstractReader],
            dict[ReaderRuntime, type[AbstractReader]],
        ] = {}
        self._uow_classes: dict[RepositoryRuntime, type[AbstractUnitOfWork]] = {}
        self._qctx_classes: dict[ReaderRuntime, type[AbstractQueryContext]] = {}

        # service and client broker registrations
        self._service_broker_factories: dict[ServiceBrokerRuntime, Callable[[BaseConfig], ServiceBroker]] = {}
        self._client_broker_factories: dict[ClientBrokerRuntime, Callable[[BaseConfig], ClientBroker]] = {}

        # command, query, and event related handlers
        self._command_handlers: list[MessageHandler] = []
        self._query_handlers: list[MessageHandler] = []
        self._event_handlers: list[MessageHandler] = []
        self._service_events: list[Event] = []
        self._client_events: list[Event] = []

        # service ports
        self._service_ports: dict[type[StegaServicePort], tuple[str, dict[RuntimeFlag, ServiceSpec]]] = {}

    def with_repository_runtime(self, runtime_field: str) -> ServiceBuilder:
        self._repo_runtime_field = runtime_field
        return self

    def with_reader_runtime(self, runtime_field: str) -> ServiceBuilder:
        self._reader_runtime_field = runtime_field
        return self

    def with_service_broker_runtime(self, runtime_field: str) -> ServiceBuilder:
        self._service_broker_runtime_field = runtime_field
        return self

    def with_client_broker_runtime(self, runtime_field: str) -> ServiceBuilder:
        self._client_broker_runtime_field = runtime_field
        return self

    def with_unit_of_work_sessions(
        self,
        factories: dict[RepositoryRuntime, Callable[[BaseConfig], Any]],
    ) -> ServiceBuilder:
        self._uow_session_factories = factories
        return self

    def with_query_context_sessions(
        self,
        factories: dict[ReaderRuntime, Callable[[BaseConfig], Any]],
    ) -> ServiceBuilder:
        self._qctx_session_factories = factories
        return self

    def with_repository(
        self,
        repo_base: type[AbstractRepository],
        repo_classes: dict[RepositoryRuntime, type[AbstractRepository]],
    ) -> ServiceBuilder:
        self._repo_classes[repo_base] = repo_classes
        return self

    def with_reader(
        self,
        reader_base: type[AbstractReader],
        reader_classes: dict[ReaderRuntime, type[AbstractReader]],
    ) -> ServiceBuilder:
        self._reader_classes[reader_base] = reader_classes
        return self

    def with_unit_of_work(
        self,
        uow_classes: dict[RepositoryRuntime, type[AbstractUnitOfWork]],
    ) -> ServiceBuilder:
        self._uow_classes = uow_classes
        return self

    def with_query_context(
        self,
        qctx_classes: dict[ReaderRuntime, type[AbstractQueryContext]],
    ) -> ServiceBuilder:
        self._qctx_classes = qctx_classes
        return self

    def with_service_broker(
        self,
        factories: dict[ServiceBrokerRuntime, Callable[[BaseConfig], ServiceBroker]],
    ) -> ServiceBuilder:
        self._service_broker_factories = factories
        return self

    def with_client_broker(
        self,
        factories: dict[ClientBrokerRuntime, Callable[[BaseConfig], ClientBroker]],
    ) -> ServiceBuilder:
        self._client_broker_factories = factories
        return self

    def with_command_handlers(self, handlers: list[MessageHandler]) -> ServiceBuilder:
        self._command_handlers = handlers
        return self

    def with_query_handlers(self, handlers: list[MessageHandler]) -> ServiceBuilder:
        self._query_handlers = handlers
        return self

    def with_event_handlers(self, handlers: list[MessageHandler]) -> ServiceBuilder:
        self._event_handlers = handlers
        return self

    def with_service_events(self, events: list[Event]) -> ServiceBuilder:
        self._service_events = events
        return self

    def with_client_events(self, events: list[Event]) -> ServiceBuilder:
        self._client_events = events
        return self

    def with_service(
        self,
        port_base: type[StegaServicePort],
        runtime_field: str,
        specs: list[ServiceSpec],
    ) -> ServiceBuilder:
        self._service_ports[port_base] = (runtime_field, {s.runtime: s for s in specs})
        return self

    def with_service_contracts(self, contracts: list[ServiceContract]) -> ServiceBuilder:
        for c in contracts:
            self.with_service(c.port_base, c.runtime_field, c.specs)
        return self

    def build(self, logger: logging.Logger) -> Service:  # noqa: C901
        # track dependencies
        deps = []

        # validate repository construction
        repo_build_settings = [
            self._uow_session_factories,
            self._repo_classes,
            self._uow_classes,
            self._repo_runtime_field,
        ]
        if any(repo_build_settings) and not all(repo_build_settings):
            msg = "All repository related constructs must be set if one is."
            raise RuntimeError(msg)

        # validate reader construction
        reader_build_settings = [
            self._qctx_session_factories,
            self._reader_classes,
            self._qctx_classes,
            self._reader_runtime_field,
        ]
        if any(reader_build_settings) and not all(reader_build_settings):
            msg = "All reader related constructs must be set if one is."
            raise RuntimeError(msg)

        # validate service broker
        service_broker_settings = [
            self._service_broker_factories,
            self._service_broker_runtime_field,
        ]
        if any(service_broker_settings) and not all(service_broker_settings):
            msg = "All service broker related constructs must be set if one is."
            raise RuntimeError(msg)

        # validate client broker
        client_broker_settings = [
            self._client_broker_factories,
            self._client_broker_runtime_field,
        ]
        if any(client_broker_settings) and not all(client_broker_settings):
            msg = "All client broker related constructs must be set if one is."
            raise RuntimeError(msg)

        # construct repositories
        if all(repo_build_settings):
            uow_session_factory = self._build_session_factory(
                self._repo_runtime_field,
                self._uow_session_factories,
            )
            repo_registry = self._build_repo_registry(
                self._repo_runtime_field,
                self._repo_classes,
            )
            uow_factory = self._build_uow_factory(
                self._repo_runtime_field,
                self._uow_classes,
            )
            deps.append(
                Dependency(
                    dep_type=AbstractUnitOfWork,
                    scope=Scope.DISPATCH,
                    provider=lambda: uow_factory(uow_session_factory, repo_registry),
                )
            )

        # construct readers
        if all(reader_build_settings):
            qctx_session_factory = self._build_session_factory(
                self._reader_runtime_field,
                self._qctx_session_factories,
            )
            reader_registry = self._build_reader_registry(
                self._reader_runtime_field,
                self._reader_classes,
            )
            qctx_factory = self._build_qctx_factory(
                self._reader_runtime_field,
                self._qctx_classes,
            )
            deps.append(
                Dependency(
                    dep_type=AbstractQueryContext,
                    scope=Scope.DISPATCH,
                    provider=lambda: qctx_factory(qctx_session_factory, reader_registry),
                )
            )

        # construct service broker
        if all(service_broker_settings):
            service_broker_factory = self._build_broker_factory(
                self._service_broker_runtime_field,
                self._service_broker_factories,
            )
            deps.append(
                Dependency(
                    dep_type=ServiceBroker, scope=Scope.SINGLETON, provider=lambda: service_broker_factory(self._config)
                )
            )

        # construct client broker
        if all(client_broker_settings):
            client_broker_factory = self._build_broker_factory(
                self._client_broker_runtime_field,
                self._client_broker_factories,
            )
            deps.append(
                Dependency(
                    dep_type=ClientBroker,
                    scope=Scope.SINGLETON,
                    provider=lambda: client_broker_factory(self._config),
                )
            )

        # construct command, event, and query registrys
        command_registry = self._build_command_registry(self._command_handlers)
        query_registry = self._build_query_registry(self._query_handlers)
        event_registry = self._build_event_registry(
            self._event_handlers,
            self._service_events,
            self._client_events,
        )

        # constrcut service ports
        for pb, (runtime_field, specs_by_flag) in self._service_ports.items():
            spec = self._select(runtime_field, specs_by_flag)
            cf = spec.channel_factory(self._config)
            tp = spec.transport_type

            def provider(
                pb: type[StegaServicePort] = pb,
                cf: Callable[[], Channel] = cf,
                tp: type[AbstractTransport] = tp,
            ) -> StegaServicePort:
                return pb(cf, tp)

            deps.append(
                Dependency(
                    dep_type=pb,
                    scope=Scope.DISPATCH,
                    provider=provider,
                )
            )

        # construct container dependencies
        container = DependencyContainer(deps)
        bus = MessageBus(
            command_registry=command_registry,
            query_registry=query_registry,
            event_registry=event_registry,
            container=container,
        )
        return Service(container=container, bus=bus, logger=logger)

    def _build_session_factory(
        self,
        runtime_field: str,
        session_factories: dict[RepositoryRuntime | ReaderRuntime, Callable[[BaseConfig], Any]],
    ) -> Callable[[BaseConfig], Any]:
        return self._select(runtime_field, session_factories)()

    def _build_repo_registry(
        self,
        runtime_field: str,
        repo_classes: dict[type[AbstractRepository], dict[RepositoryRuntime, type[AbstractRepository]]],
    ) -> RepositoryRegistry:
        registry = RepositoryRegistry()
        for repo_base, repo_concrete_mapping in repo_classes.items():
            repo_concrete = self._select(runtime_field, repo_concrete_mapping)
            registry.register(repo_base, repo_concrete)
        registry.freeze()
        return registry

    def _build_uow_factory(
        self,
        runtime_field: str,
        uow_classes: dict[RepositoryRuntime, type[AbstractUnitOfWork]],
    ) -> AbstractUnitOfWork:
        return self._select(runtime_field, uow_classes)

    def _build_reader_registry(
        self,
        runtime_field: str,
        reader_classes: dict[
            type[AbstractReader],
            dict[ReaderRuntime, type[AbstractReader]],
        ],
    ) -> ReaderRegistry:
        registry = ReaderRegistry()
        for reader_base, reader_concrete_mapping in reader_classes.items():
            reader_concrete = self._select(runtime_field, reader_concrete_mapping)
            registry.register(reader_base, reader_concrete)
        registry.freeze()
        return registry

    def _build_qctx_factory(
        self,
        runtime_field: str,
        qctx_classes: dict[ReaderRuntime, type[AbstractQueryContext]],
    ) -> AbstractQueryContext:
        return self._select(runtime_field, qctx_classes)

    def _build_broker_factory(
        self,
        runtime_field: str,
        broker_factories: dict[
            ServiceBrokerRuntime | ClientBrokerRuntime,
            Callable[[BaseConfig], ServiceBroker | ClientBroker],
        ],
    ) -> Callable[[BaseConfig], ServiceBroker | ClientBroker]:
        return self._select(runtime_field, broker_factories)

    def _build_command_registry(self, command_handlers: list[MessageHandler]) -> CommandRegistry:
        registry = CommandRegistry()
        for handler in command_handlers:
            binding = bind_handler(handler, Command)
            registry.register(binding.msg_type, binding)
        registry.freeze()
        return registry

    def _build_query_registry(self, query_handlers: list[MessageHandler]) -> QueryRegistry:
        registry = QueryRegistry()
        for handler in query_handlers:
            binding = bind_handler(handler, Query)
            registry.register(binding.msg_type, binding)
        registry.freeze()
        return registry

    def _build_event_registry(
        self,
        event_handlers: list[MessageHandler],
        service_events: list[type[Event]],
        client_events: list[type[Event]],
    ) -> EventRegistry:
        registry = EventRegistry()

        for event_type in service_events:
            handler = make_service_publish_handler(event_type)
            binding = bind_handler(handler, Event)
            registry.register(binding.msg_type, binding)

        for event_type in client_events:
            handler = make_client_publish_handler(event_type)
            binding = bind_handler(handler, Event)
            registry.register(binding.msg_type, binding)

        for handler in event_handlers:
            binding = bind_handler(handler, Event)
            registry.register(binding.msg_type, binding)

        registry.freeze()
        return registry

    def _select(self, runtime_field: str, mapping: dict) -> Any:  # noqa: ANN401
        set_runtime = getattr(self._config, runtime_field)
        if set_runtime is None:
            err_msg = f"{runtime_field} must be set as a config value"
            raise RuntimeError(err_msg)
        is_set_runtime_flag = isinstance(set_runtime, Flag)
        for available_runtime, selectable in mapping.items():
            if is_set_runtime_flag and isinstance(available_runtime, Flag):
                if set_runtime & available_runtime:
                    return selectable
            elif set_runtime == available_runtime:
                return selectable
        err_msg = f"Set runtime {set_runtime:!r} not possible option"
        raise ValueError(err_msg)


class Service:
    def __init__(
        self,
        container: DependencyContainer,
        bus: MessageBus,
        logger: logging.Logger,
    ) -> None:
        self._container = container
        self._bus = bus
        self._logger = logger
        self._service_broker: ServiceBroker | None = self._resolve_broker(ServiceBroker)
        self._client_broker: ClientBroker | None = self._resolve_broker(ClientBroker)

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @property
    def bus(self) -> MessageBus:
        return self._bus

    @property
    def service_broker(self) -> ServiceBroker:
        if self._service_broker is None:
            msg = "No service broker exists for this service"
            raise RuntimeError(msg)
        return self._service_broker

    @property
    def client_broker(self) -> ClientBroker:
        if self._client_broker is None:
            msg = "No client broker exists for this service"
            raise RuntimeError(msg)
        return self._client_broker

    @asynccontextmanager
    async def lifespan(self) -> Iterator[Service]:
        service_broker = self._service_broker
        client_broker = self._client_broker
        bus = self.bus

        if service_broker is not None:
            await service_broker.start()
        if client_broker is not None:
            await client_broker.start()
        await bus.start()
        try:
            yield self
        finally:
            await bus.stop()
            if client_broker is not None:
                await client_broker.stop()
            if service_broker is not None:
                await service_broker.stop()

    def _resolve_broker(self, broker_cls: type[ServiceBroker | ClientBroker]) -> ServiceBroker | ClientBroker | None:
        try:
            return self._container.resolve_singleton(broker_cls)
        except KeyError:
            pass
        return None
