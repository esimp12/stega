"""Module for initializing the application runtime under the given environment."""

import functools
import inspect
import typing as T

from stega_lib.domain import Command, CommandType

from stega_core.ports.base import ServiceType
from stega_core.services.handlers.mapping import (
    COMMAND_HANDLERS,
    CommandHandlerType,
    PrimitiveType,
    EVENT_HANDLERS,
)
from stega_core.services.messagebus import MessageBus


ServiceHandlers = dict[CommandType, T.Callable[[Command], PrimitiveType]]


class Dispatcher:
    """Class for dispatching commands to associated service calls."""

    def __init__(self, handlers: ServiceHandlers) -> None:
        """Inits a Dispatcher."""
        self._handlers = handlers

    def handle(self, cmd: Command) -> PrimitiveType:
        """Dispatches a command to associated service and processes it accordingly.

        Args:
            cmd: A Commmand to dispatch to a service.

        Returns:
            A PrimitiveType of the result of the commands service call.
        """
        cmd_type = type(cmd)
        if cmd_type not in self._handlers:
            err_msg = f"Command type {cmd_type} unknown!"
            raise ValueError(err_msg)
        return self._handlers[cmd_type](cmd)


def bootstrap_dispatcher(
    services: list[ServiceType],
) -> Dispatcher:
    """Provisions the application with the selected runtime service ports.

    Args:
        services: A list of service ports to provision.

    Returns:
        A Dispatcher for mapping commands to their respective service handlers.

    """
    dependencies = {"services": services}
    handlers = {
        command_type: inject_dependencies(handler, dependencies) for command_type, handler in COMMAND_HANDLERS.items()
    }
    return Dispatcher(handlers=handlers)


def bootstrap_event_bus() -> MessageBus:
    """Provisions the application with the selected event consumers.

    Returns:
        A MessageBus for mapping events to their respective service handlers.

    """
    return MessageBus(event_handlers=EVENT_HANDLERS)


def inject_dependencies(
    handler: CommandHandlerType,
    dependencies: dict[str, list[ServiceType]],
) -> T.Callable[[Command], PrimitiveType]:
    """Inject runtime dependencies for service handlers.

    Args:
        handler: A Callable of a service handler without any runtime dependencies
            injected yet.
        dependencies: A Mapping of shared runtime kwargs to inject into service
            handlers.

    Returns:
        A Callable of a service handler with a Command as the sole argument.
    """

    def _get_service_parent_class(service: ServiceType) -> type[ServiceType]:
        return service.__class__.__bases__[0]

    deps = {}
    params = inspect.signature(handler).parameters
    service_types = {_get_service_parent_class(service): service for service in dependencies.get("services", [])}
    for name, param in params.items():
        # Inject normal dependencies
        if param.annotation not in service_types:
            if name in dependencies and name != "services":
                deps[name] = dependencies[name]
        # Inject service dependencies based on the type provided
        # NOTE: This allows us to provide generic service parameter names for handlers so that we don't have to
        # know the common argument names for each service function and they don't have to be unique.
        else:
            deps[name] = service_types[param.annotation]
    return functools.partial(handler, **deps)
