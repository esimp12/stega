from dataclasses import dataclass


@dataclass
class Command:
    """Action for CLI daemon to handle."""


@dataclass
class ReadCommand(Command):
    """Command for read actions."""


@dataclass
class WriteCommand(Command):
    """Command for write actions.

    Attributes:
        correlation_id: A globally unique str representing an event trace
            occuring throughout the system.

    """

    correlation_id: str


@dataclass
class GetPortfolio(ReadCommand):
    """Command to fetch a portfolio.

    Attributes:
        portfolio_id: A str of the unique ID of the portfolio.

    """

    portfolio_id: str


@dataclass
class ListPortfolios(ReadCommand):
    """Command to list portfolios."""


@dataclass
class CreatePortfolio(WriteCommand):
    """Command to create a new portfolio.

    Attributes:
        name: A str of the portfolio name.
        assets: A list of portfolio assets as dict instances. An asset contains
            both a symbol and a weight.

    """

    name: str
    assets: dict[str, float]
