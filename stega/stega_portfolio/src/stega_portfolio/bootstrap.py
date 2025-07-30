"""Module for initializing the application runtime under the given environment."""

import functools
import inspect
import typing as T

from stega_portfolio.ports.orm import start_mappers
from stega_portfolio.services.handlers.mapping import COMMAND_HANDLERS, EVENT_HANDLERS
from stega_portfolio.services.messagebus import Message, MessageBus
from stega_portfolio.services.uow.base import AbstractUnitOfWork


def bootstrap(
    uow: AbstractUnitOfWork,
    *,
    start_orm: bool = True,
) -> MessageBus:
    """Provisions the application with the selected runtime adapters.

    Args:
        uow: An AbstractUnitOfWork instance to manage service transaction sessions.
        start_orm: A boolean to enable or disable creating ORM mappers.

    Returns:
        A MessageBus instance with the given unit of work injected.

    """
    if start_orm:
        start_mappers()

    dependencies = {"uow": uow}
    injected_command_handlers = {
        command_type: inject_dependencies(handler, dependencies) for command_type, handler in COMMAND_HANDLERS.items()
    }
    injected_event_handlers = {
        event_type: inject_dependencies(handler, dependencies) for event_type, handler in EVENT_HANDLERS.items()
    }

    return MessageBus(uow=uow, command_handlers=injected_command_handlers, event_handlers=injected_event_handlers)


def inject_dependencies(
    handler: T.Callable[[Message, AbstractUnitOfWork], None],
    dependencies: dict[str, AbstractUnitOfWork],
) -> T.Callable[[Message], None]:
    """Inject runtime dependencies for service handlers.

    Args:
        handler: A Callable of a service handler without any runtime dependencies
            injected yet.
        dependencies: A Mapping of shared runtime kwargs to inject into service
            handlers.

    Returns:
        A Callable of a service handler with a Message as the sole argument.

    """
    params = inspect.signature(handler).parameters
    deps = {name: dependency for name, dependency in dependencies.items() if name in params}
    return functools.partial(handler, **deps)
