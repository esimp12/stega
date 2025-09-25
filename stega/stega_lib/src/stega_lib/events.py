"""Module for common event types used across the stega application."""

from __future__ import annotations

import typing as T


class Event:
    """Base class for all events."""

    topic: str = "events"

    events_mapping: dict[str, T.Type[Event]] = {
        event_type.topic: event_type
        for event_type in [
            PortfolioCreated,
            PortfolioUpdated,
            PortfolioDeleted,
        ]
    }

    @classmethod
    def from_message(cls, topic: str, body: dict[str, T.Any]) -> Event:
        """Create an Event from its topic and incoming raw message.
        
        Args:
            topic (str): The event topic to source an event for.
            body (Mapping): The raw event message to extract into event args.

        Returns:
            An Event to process.

        """
        if topic not in cls.events_mapping:
            err_msg = f"'{topic}' is not a recognized event topic"
            raise ValueError(err_msg)

        event_type = cls.events_mapping[topic]
        return event_type(**body)


class PortfolioCreated(Event):
    """Event indicating that a portfolio has been created.

    Attributes:
        id: The unique identifier of the created portfolio.
    """

    topic: str = "events.portfolio.created"

    def __init__(
        self,
        id: str,  # noqa: A002
    ) -> None:
        """Initialize the PortfolioCreated event."""
        self.id = id


class PortfolioDeleted(Event):
    """Event indicating that a portfolio has been deleted.

    Attributes:
        id: The unique identifier of the deleted portfolio.
    """

    topic: str = "events.portfolio.deleted"

    def __init__(
        self,
        id: str,  # noqa: A002
    ) -> None:
        """Initialize the PortfolioDeleted event."""
        self.id = id


class PortfolioUpdated(Event):
    """Event indicating that a portfolio has been updated.

    Attributes:
        id: The unique identifier of the updated portfolio.
    """

    topic: str = "events.portfolio.updated"

    def __init__(
        self,
        id: str,  # noqa: A002
    ) -> None:
        """Initialize the PortfolioUpdated event."""
        self.id = id

