from stega_cli.domain.command import Command 
from stega_cli.services.handlers.mapping import (
    COMMAND_HANDLERS,
    CommandHandler,
    ResponseType,
)


class Dispatcher:
    """Class for dispatching commands to associated service calls."""

    def __init__(self, handlers: ServiceHandlers) -> None:
        """Inits a Dispatcher."""
        self._handlers = handlers

    def handle(self, cmd: Command) -> ResposneType:
        """Dispatches a command to associated service and processes it accordingly.

        Args:
            cmd: A Commmand to dispatch to a service.

        Returns:
            A ResponseType of the result of the commands service call.
        """
        cmd_type = type(cmd)
        if cmd_type not in self._handlers:
            err_msg = f"Command type {cmd_type} unknown!"
            raise ValueError(err_msg)
        return self._handlers[cmd_type](cmd)


def bootstrap_dispatcher() -> Dispatcher:
    """Provisions the application with the selected runtime service ports.

    Returns:
        A Dispatcher for mapping commands to their respective service handlers.

    """
    return Dispatcher(handlers=COMMAND_HANDLERS)

