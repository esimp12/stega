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
)

from stega_core.message import (
    Message,
    MessageResponse,
)

if TYPE_CHECKING:
    from collections.abc import Callable


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

        self._singletons: dict[type, object] = {d.dep_type: d.provider() for d in deps if d.scope is Scope.SINGLETON}

    def __contains__(self, dep_type: type) -> bool:
        return dep_type in self._deps

    def dispatch_scope(self) -> DispatchScope:
        return DispatchScope(self)

    def resolve_singleton[DepT](self, dep_type: type[DepT]) -> DepT:
        if dep_type not in self._singletons:
            err_msg = f"No singleton registered for {dep_type.__name__} (available: {list(self._singletons.keys())})"
            raise KeyError(err_msg)
        return cast("DepT", self._singletons[dep_type])

    def get_dependency[DepT](self, dep_type: type[DepT]) -> Dependency[DepT]:
        dep = self._deps.get(dep_type)
        if dep is None:
            err_msg = f"No dependency registered for {dep_type.__name__}"
            raise KeyError(err_msg)
        return cast("Dependency[DepT]", dep)


class DispatchScope:
    def __init__(self, container: DependencyContainer) -> None:
        self._container = container
        self.resolved = dict[type, object] = {}

    def resolve[DepT](self, dep_type: type[DepT]) -> DepT:
        dep = self._container.get_dependency(dep_type)

        if dep.scope is Scope.SINGLETON:
            return self._container.resolve_singleton(dep_type)

        if dep_type not in self.resolved:
            self.resolved[dep_type] = dep.provider()
        return cast("DepT", self.resolved[dep_type])


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
    required_types: dict[str, type] = {}
    params = params[1:]  # skip first type annotation
    for p in params:
        annotation = hints.get(p.name)
        if annotation is None:
            err_msg = (
                f"Handler {handler.__qualname__} parameter '{p.name}' has no type annotation; "
                "type-based DI requires annotations on all injected parameters"
            )
            raise TypeError(err_msg)
        required_types[p.name] = annotation

    return MessageHandlerBinding(
        handler=handler,
        msg_type=msg_type,
        dep_types=required_types,
    )
