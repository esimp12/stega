import asyncio
from dataclasses import dataclass
from typing import cast

from stega_lib.core.command import Core
from stega_lib.core.event import Event, EventDispatch
from stega_lib.core.query import Query
from stega_lib.core.response import (
    Response,
    CommandResponse,
    QueryResponse,
    QueryStatus,
    SubmissionStatus,
)
from stega_lib.di import DependencyContainer, DispatchScope, Action, HandlerBinding
from stega_lib.messaging import CommandRegistry, QueryRegistry, EventRegistry


@dataclass(frozen=True)
class BusConfig:
    worker_count: int = 1
    async_queue_maxsize: int = 0 shutdown_timeout_seconds: float = 30.0


class MessageBus:

    def __init__(
        self,
        command_registry: CommandRegistry,
        query_registry: QueryRegistry,
        event_registry: EventRegistry,
        container: DependencyContainer,
        config: BusConfig | None = None,
    ) -> None:
        self._commands = command_registry
        self._queries = query_registry
        self._events = event_registry
        self._container = container
        self._config = config or BusConfig()
    
        self._async_queue: asyncio.Queue[Event] = asyncio.Queue(
            maxsize=self._config.async_queue_maxsize,
        )
        self._workers = list[asyncio.Task] = []
        self._running = False

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._workers = [
            asyncio.create_task(self._worker_loop(worker_id=i), name=f"event-worker-{id}")
            for i in range(self._config.worker_count)
        ]

    async def stop(self) -> None:
        if not self._running:
            return
        self._running = False

        # wait for queue events to process or automatically shutdown after timeout
        try:
            await asyncio.wait_for(
                self._async_queue.join(),
                timeout=self._config.shutdown_timeout_seconds,
            )
        except asyncio.TimeoutError:
            pass
        
        # cancel workers
        for worker in self._workers:
            worker.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers = []

    async def handle_command(self, command: Command) -> CommandResponse:
        cmd_type = type(command)
        binding = self._commands.get(cmd_type)
        if binding is None:
            return CommandResponse(
                status=SubmissionStatus.FAILED,
                error=f"No handler registered for {cmd_type.__name__}"),
            )

        try:
            response, scope = await self._invoke(binding, command, CommandResponse) 
        except Exception as exc:
            return CommandResponse(
                status=SubmissionStatus.FAILED,
                error=f"{type(exc).__name__}: {exc}",
            )

        for event in self._drain_events(scope):
            await self.handle_event(event)

        return response

    async def handle_query[TView: View](self, query: Query[TView]) -> QueryResponse[TView]:
        query_type = type(query)
        binding = self._queries.get(query_type)
        if binding is None:
            return QueryResponse(
                status=QueryStatus.FAILED,
                error=f"No handler registered for {query_type.__name__}",
            )

        try:
            response, _ = await self._invoke(binding, query, QueryResponse)
            return response
        except Exception as exc:
            return QueryResponse(
                status=QueryStatus.FAILED,
                error=f"{type(exc).__name__}: {exc}",
            )

    async def handle_event(self, event: Event) -> None:
        if event.dispatch is EventDispatch.ASYNC:
            await self._async_queue.put(event)
            return

        sync_queue: list[Event] = [event]
        while sync_queue:
            current = sync_queue.pop(0)
            cascaed = await self._dispatch_event_locally(current)
            for next_event in cascaded:
                if next_event.dispatch is EventDispatch.ASYNC:
                    await self._async_queue.put(event)
                else:
                    sync_queue.append(next_event)

    async def _invoke[TResponse: Response | None](
        self,
        binding: HandlerBinding,
        action: Action, 
        response_type: type[TResponse],
    ) -> tuple[TResponse, DispatchScope]:
        scope = self._container.dispatch_scope()
        deps = {
            name: scope.resolve(t)
            for name, t in binding.dep_types.items()
        }
        result = await binding.handler(action, **deps)

        if not isinstance(result, response_type):
            err_msg = (
                f"Handler {binding.handler.__qualname__} returned {type(result).__name__}, "
                f"expected {response_type.__name__}"
            )
            raise TypeError(err_msg)

        return cast(TResponse, result), scope

    async def _dispatch_event_locally(self, event: Event) -> list[Event]:
        bindings = self._events.get(type(event))
        if not bindings:
            return []
       
        NoneType = type(None)
        cascaded: list[Event] = []
        for binding in bindings:
            try:
                result, scope = await self._invoke(binding, event, NoneType)
                cascaded.extend(self._drain_events(scope))
            except Exception:
                pass
        return cascaded

    def _drain_events(self, scope: DispatchScope) -> list[Event]:
        uow = scope.resolve(AbstractUnitOfWork)
        if uow is None:
            return []
        return list(uow.collect_new_events())

    async def _worker_loop(self, worker_id: int) -> None:
        try:
            while True:
                event = await self._async_queue.get()
                try:
                    sync_queue: list[Event] = [event]
                    while sync_queue:
                        current = sync_queue.pop(0)
                        cascaded = await self._dispatch_event_locally(current)
                        for next_event in cascaded:
                            if next_event.dispatch is EventDispatch.ASYNC:
                                await self._async_queue.put(next_event)
                            else:
                                sync_queue.append(next_event)
                except Exception:
                    pass
                finally:
                    self._async_queue.task_done()
        except asyncio.CancelledError:
            raise
