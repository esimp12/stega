from stega_cli.domain.command import Command
from stega_cli.domain.request import Response
from stega_cli.services.handlers.mapping import (
    COMMAND_HANDLERS,
    CommandHandlers,
)


class CommandDispatcher:
    """Class for dispatching commands to associated service calls."""

    def __init__(self, handlers: CommandHandlers) -> None:
        """Inits a Dispatcher."""
        self._handlers = handlers

    def handle(self, cmd: Command) -> Response | None:
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


def bootstrap_cmd_dispatcher() -> CommandDispatcher:
    """Provisions the application with the selected runtime service ports.

    Returns:
        A CommandDispatcher for mapping commands to their respective service handlers.

    """
    return CommandDispatcher(handlers=COMMAND_HANDLERS)
