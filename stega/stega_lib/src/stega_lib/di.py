from __future__ import annotations

import inspect
from dataclasses import dataclass
from enum import Enum
from typing import (
    Any,
    Awaitable,
    Callable,
    Protocol,
    get_type_hints,
    cast,
)

from stega_lib.core.command import Command
from stega_lib.core.event import Event
from stega_lib.core.query import Query
from stega_lib.core.response import Resposne


type Action = Command | Query | Event


class Scope(Enum):
    DISPATCH: str = "dispatch"
    SINGLETON: str = "singleton"


@dataclass(frozen=True)
class Dependency[TDep]:
    dep_type: type[TDep]
    scope: Scope
    provider: Callable[[], TDep]


class ActionHandler[TAction: Action, TResponse: Response | None](Protocol):
    async def __call__(self, action: TAction, /, **kwargs: Any) -> TResponse: ...


@dataclass(frozen=True)
class HandlerBinding[TAction: Action, TResponse: Response | None]:
    handler: ActionHandler[TAction, TResponse]
    action_type: type[TAction]
    dep_types: dict[str, type]


class DependencyContainer:

    def __init__(self, deps: list[Dependency]) -> None:
        self._deps: dict[type, Dependency] = {}
        for d in deps:
            if d.dep_type in self._deps:
                err_msg = f"Dependency already registered for {d.dep_type.__name__}"
                raise ValueError(err_msg)
            self._deps[d.dep_type] = d
        
        self._singletons: dict[type, object] = {
            d.dep_type: d.provider()
            for d in deps
            if d.scope is Scope.SINGLETON
        }

    def __contains__(self, dep_type: type) -> bool:
        return dep_type in self._deps

    def dispatch_scope(self) -> DispatchScope:
        return DispatchScope(self)

    def resolve_singleton[T](self, dep_type: type[T]) -> T:
        if dep_type not in self._singletons:
            err_msg = f"No singleton registered for {dep_type.__name__} (available: {list(self._singletons.keys())})"
            raise KeyError(err_msg)
        return cast(T, self._singletons[dep_type])

    def get_dependency[T](self, dep_type: type[T]) -> Dependency[T]:
        dep = self._deps.get(dep_type)
        if dep is None:
            err_msg = f"No dependency registered for {dep_type.__name__}"
            raise KeyError(err_msg)
        return cast(Dependency[T], dep)


class DispatchScope:

    def __init__(self, container: DependencyContainer) -> None:
        self._container = container
        self.resolved = dict[type, object] = {}

    def resolve[T](self, dep_type: type[T]) -> T:
        dep = self._container.get_dependency(dep_type)
        
        if dep.scope is Scope.SINGLETON:
            return self._container.resolve_singleton(dep_type)

        if dep_type not in self.resolved:
            self.resolved[dep_type] = dep.provider()
        return cast(T, self.resolved[dep_type])


def bind_handler[TAction, TResponse](
    handler: ActionHandler[TAction, TResponse],
    container: DependencyContainer, 
    expected_action_base: type[TAction],
) -> HandlerBinding[TAction, TResponse]:
    sig = inspect.signature(handler)
    hints = get_type_hints(sig)
    params = list(sig.parameters.values())
    if not params:
        err_msg = f"{handler.__qualname__} must accept an action parameter"
        raise TypeError(err_msg)
    
    # enforce expected_action_base as first handler arg, e.g. def handler(action: ActionType, ...)
    action_param = params[0]
    action_type = hints.get(action_param.name)
    if action_type is None:
        err_msg = f"{handler.__qualname__} action parameter must be annotated"
        raise TypeError(err_msg)
    if not (isinstance(action_type, type) and issubclass(action_type, expected_action_base)):
        err_msg = (
            f"{handler.__qualname__} action parameter type {action_type} "
            f"is not a subclass of {expected_action_base.__name__}"
        )
        raise TypeError(err_msg)

    # resolve parameter types by their annotations
    required_types: dict[str, type] = {}
    params = params[1:] # skip first action_type annotation
    for p in params:
        annotation = hints.get(p.name)
        if annotation is None:
            err_msg = (
                f"Handler {handler.__qualname__} parameter '{p.name}' has no type annotation; "
                "type-based DI requires annotations on all injected parameters"
            )
            raise TypeError(err_msg)
        required_types[p.name] = annotation

    return HandlerBinding(handler=handler, action_type=action_type, dep_types=required_types)
