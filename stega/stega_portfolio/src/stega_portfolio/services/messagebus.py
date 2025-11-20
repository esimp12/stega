"""A messaging layer responsible for ingesting, routing, and resolving messages."""

import typing as T

from stega_lib.domain import Command
from stega_lib.events import Event

from stega_portfolio.config import create_config, create_logger
from stega_portfolio.domain.errors import PortfolioAppError
from stega_portfolio.services.handlers.mapping import CommandType, EventType
from stega_portfolio.services.uow.base import AbstractUnitOfWork

Message = Command | Event


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
        command_handlers: dict[CommandType, T.Callable[[Command], None]],
        event_handlers: dict[EventType, list[T.Callable[[Event], None]]],
    ) -> None:
        """Initialize the MessageBus."""
        self.uow = uow
        self.command_handlers = command_handlers
        self.event_handlers = event_handlers
        self.queue = []
        self.config = create_config()
        self.logger = create_logger(self.config)

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
            elif isinstance(message, Event):
                self.handle_event(message)
            else:
                err_msg = f"Message {message} is not a Message"
                raise TypeError(err_msg)

    def handle_command(self, command: Command) -> None:
        """Process a Command by routing it to the appropriate service handler.

        Args:
            command: A Command instance to submit to a service handler.

        """
        command_type = type(command)
        try:
            handler = self.command_handlers[command_type]
            handler(command)
            self.queue.extend(self.uow.collect_new_events())
        # Warn when expected application errors occur
        except PortfolioAppError:
            self.logger.warning("Application error occurred while handling command %s", command_type)
            raise
        # Indicate exceptions when unexpected errors occur
        except Exception:
            self.logger.exception("Failed to handle command %s", command_type)
            raise

    def handle_event(self, event: Event) -> None:
        """Process an Event by routing it to the appropriate service handler.

        Args:
            event: An Event instance to submit to a service handler.

        """
        event_type = type(event)
        for handler in self.event_handlers[event_type]:
            try:
                handler(event)
                self.queue.extend(self.uow.collect_new_events())
            except PortfolioAppError:
                self.logger.warning("Application error occurred while handling event %s", event_type)
                continue
            except Exception:
                self.logger.exception("Failed to handle event %s", event_type)
                continue
