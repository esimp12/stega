from __future__ import annotations

import inspect
from dataclasses import dataclass
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    Protocol,
    cast,
    get_type_hints,
    runtime_checkable,
)

from stega_core.message import (
    Message,
    MessageResponse,
)

if TYPE_CHECKING:
    from collections.abc import Callable


@runtime_checkable
class Lifecyle(Protocol):
    async def start(self) -> None:
        ...
    async def stop(self) -> None:
        ...


class Scope(Enum):
    DISPATCH: str = "dispatch"
    SINGLETON: str = "singleton"


@dataclass(frozen=True)
class Dependency[DepT]:
    dep_type: type[DepT]
    scope: Scope
    provider: Callable[[], DepT]


class MessageHandler[MessageT: Message, MessageResponseT: MessageResponse](Protocol):
    async def __call__(self, msg: MessageT, /, **kwargs: Any) -> MessageResponseT: ...  # noqa: ANN401


@dataclass(frozen=True)
class MessageHandlerBinding[MessageT: Message, MessageResponseT: MessageResponse]:
    handler: MessageHandler[MessageT, MessageResponseT]
    msg_type: type[MessageT]
    dep_types: dict[str, type]


class DependencyContainer:
    def __init__(self, deps: list[Dependency]) -> None:
        self._deps: dict[type, Dependency] = {}
        for d in deps:
            if d.dep_type in self._deps:
                err_msg = f"Dependency already registered for {d.dep_type.__name__}"
                raise ValueError(err_msg)
            self._deps[d.dep_type] = d

        self._singletons: dict[type, object] = {}
        self._building: set[type] = set()
        for dep_type, dep in self._deps.items():
            if dep.scope is Scope.SINGLETON:
                self.resolve_singleton(dep_type)

    def __contains__(self, dep_type: type) -> bool:
        return dep_type in self._deps

    def dispatch_scope(self) -> DispatchScope:
        return DispatchScope(self)

    def instantiate[DepT](self, dep: Dependency[DepT], resolve: Callable[[type], Any]) -> DepT:
        param_types = annotated_param_types(dep.provider)
        if not param_types:
            return dep.provider()
        return dep.provider(**{name: resolve(t) for name, t in param_types.items()})

    def resolve_singleton[DepT](self, dep_type: type[DepT]) -> DepT:
        if dep_type in self._singletons:
            return cast("DepT", self._singletons[dep_type])
        dep = self._deps.get(dep_type)
        if dep is None or dep.scope is not Scope.SINGLETON:
            err_msg = f"No singleton registered for {dep_type.__name__}"
            raise KeyError(err_msg)
        if dep_type in self._building:
            err_msg = f"Singleton dependency cycle at {dep_type.__name__}"
            raise RuntimeError(err_msg)
        self._building.add(dep_type)
        instance = self.instantiate(dep, self.resolve_singleton)
        self._building.discard(dep_type)
        self._singletons[dep_type] = instance
        return cast("DepT", instance)

    def lifecycle_singletons(self) -> list[Lifecycle]:
        order = self._singleton_start_order()
        resources: list[Lifecyle] = []
        for dep_type in order:
            instance = self.resolve_singleton(dep_type)
            if isinstance(instance, Lifecycle):
                resources.append(instance)
        return resources

    def get_dependency[DepT](self, dep_type: type[DepT]) -> Dependency[DepT]:
        dep = self._deps.get(dep_type)
        if dep is None:
            err_msg = f"No dependency registered for {dep_type.__name__}"
            raise KeyError(err_msg)
        return cast("Dependency[DepT]", dep)

    def _singleton_start_order(self) -> list[type]:
        singletons = [d for d in self._deps if d.scope is Scope.SINGLETON]
        index = {d.dep_type: i for i, d in enumerate(singletons)}
        indegree = {d.dep_type: 0 for d in singletons}
        adj: dict[type, list[type]] = {d.dep_type: [] for d in singletons}

        for dep in singletons:
            for req in dep.requires:
                if req not in indegree:
                    continue
                adj[req].append(dep.dep_type)
                indegree[dep.dep_type] += 1

        ready = deque(sorted((t for t, n in indegree.items() if n == 0), key=index.__getitem__))
        order: list[type] = []
        while ready:
            none = ready.popleft()
            order.append(node)
            freed = []
            for nxt in adj[node]:
                indegree[nxt] -= 1
                if indegree[nxt] == 0:
                    freed.append(nxt)
            for nxt in sorted(freed, key=index.__getitem__):
                ready.append(nxt)

        if len(order) != len(singletons):
            cycle = sorted(t.__name__ for t, n in indegree.items() if n > 0)
            err_msg = f"Dependency cycle among singletons: {cycle}"
            raise RuntimeError(err_msg)
        return order


class DispatchScope:
    def __init__(self, container: DependencyContainer) -> None:
        self._container = container
        self.resolved: dict[type, object] = {}

    def resolve[DepT](self, dep_type: type[DepT]) -> DepT:
        dep = self._container.get_dependency(dep_type)
        if dep.scope is Scope.SINGLETON:
            return self._container.resolve_singleton(dep_type)
        if dep_type in self.resolved:
            return cast("DepT", self.resolved[dep_type])
        if dep_type in self._building:
            err_msg = f"Dispatch dependency cycle at {dep_type.__name__}"
            raise RuntimeError(err_msg)
        self._building.add(dep_type)
        instance = self._container.instantiate(dep, self.resolve)
        self._building.discard(dep_type)
        self.resolved[dep_type] = instance
        return cast("DepT", instance)


def bind_handler[MessageT, MessageResponseT](
    handler: MessageHandler[MessageT, MessageResponseT],
    expected_msg_base: type[MessageT],
) -> MessageHandlerBinding[MessageT, MessageResponseT]:
    sig = inspect.signature(handler)
    hints = get_type_hints(handler)
    params = list(sig.parameters.values())
    if not params:
        err_msg = f"{handler.__qualname__} must accept a message parameter"
        raise TypeError(err_msg)

    # enforce expected base as first handler arg, e.g. def handler(msg: Message, ...)
    msg_param = params[0]
    msg_type = hints.get(msg_param.name)
    if msg_type is None:
        err_msg = f"{handler.__qualname__} message parameter must be annotated"
        raise TypeError(err_msg)
    if not (isinstance(msg_type, type) and issubclass(msg_type, expected_msg_base)):
        err_msg = (
            f"{handler.__qualname__} message parameter type {msg_type} "
            f"is not a subclass of {expected_msg_base.__name__}"
        )
        raise TypeError(err_msg)

    # resolve parameter types by their annotations
    required_types = annotated_param_types(handler, skip=1)

    return MessageHandlerBinding(
        handler=handler,
        msg_type=msg_type,
        dep_types=required_types,
    )


def annotated_param_types(fn: Callable[..., Any], *, skip: int = 0) -> dict[str, type]:
    params = list(inspect.signature(fn).parameters.values())[skip:]
    if not params:
        return {}
    hints = get_type_hints(fn)
    out: dict[str, type] = {}
    for p in params:
        ann = hints.get(p.name)
        if ann is None:
            err_msg = (
                f"{getattr(fn, '__qualname__', fn)!r} parameter '{p.name}' has no type annotation; "
                "type-based DI requires annotations on all injected parameters"
            )
            raise TypeError(err_msg)
        out[p.name] = ann
    return out
