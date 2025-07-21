"""A messaging layer responsible for ingesting, routing, and resolving messages."""

import typing as T

from stega_lib.domain import Command

from stega_portfolio.services.handlers.mapping import CommandType
from stega_portfolio.services.uow.base import AbstractUnitOfWork

Message = Command


class MessageBus:
    """Maps domain commands and events to service handlers.

    Attributes:
        uow: An AbstractUnitOfWork to inject in all command and event handlers.
        command_handlers: A mapping of Command types to their respective service
            handlers.
        queue: A list of Message instances to distribute to handlers.

    """

    def __init__(
        self,
        uow: AbstractUnitOfWork,
        command_handlers: T.Mapping[CommandType, T.Callable[[Command], T.Any]],
    ) -> None:
        """Initialize the MessageBus."""
        self.uow = uow
        self.command_handlers = command_handlers
        self.queue = []

    def handle(self, message: Message) -> None:
        """Process a Message by routing it to the appropriate service handler.

        Args:
            message: A Message instance to submit to a service handler.

        Raises:
            A TypeError if message is not a Command or Event.

        """
        self.queue = [message]
        while self.queue:
            message = self.queue.pop(0)
            if isinstance(message, Command):
                self.handle_command(message)
            else:
                err_msg = f"Message {message} is not a Message"
                raise TypeError(err_msg)

    def handle_command(self, command: Command) -> None:
        """Process a Command by routing it to the appropriate service handler.

        Args:
            command: A Command instance to submit to a service handler.

        """
        handler = self.command_handlers[type(command)]
        handler(command)
