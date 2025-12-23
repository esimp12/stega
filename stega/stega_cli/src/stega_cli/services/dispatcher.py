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
        command_type: inject_dispatcher_dependencies(handler, dependencies)
        for command_type, handler in COMMAND_HANDLERS.items()
    }
    return Dispatcher(handlers=handlers)


