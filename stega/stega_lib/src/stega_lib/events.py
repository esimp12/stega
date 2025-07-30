"""Module for common event types used across the stega application."""


class Event:
    """Base class for all events."""

    topic: str = "events"


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
