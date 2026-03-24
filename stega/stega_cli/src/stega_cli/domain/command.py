from dataclasses import dataclass


@dataclass
class Command:
    pass


@dataclass
class ReadCommand(Command):
    pass


@dataclass
class WriteCommand(Command):
    correlation_id: str


@dataclass
class GetPortfolio(ReadCommand):
    portfolio_id: str


@dataclass
class ListPortfolios(ReadCommand):
    pass


@dataclass
class CreatePortfolio(WriteCommand):
    name: str
    assets: dict[str, float]
