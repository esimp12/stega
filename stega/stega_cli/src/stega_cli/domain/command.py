from dataclasses import dataclass, asdict
import typing as T


@dataclass
class Response:
    """Response to send ack back from CLI daemon."""

    status: str
    result: dict[str, T.Any]

    def to_json(self) -> dict[str, T.Any]:
        return {
            "status": self.status,
            "result": self.result,
        }


@dataclass
class Command:
    """Command to send to CLI daemon."""
    
    def to_json(self) -> dict[str, T.Any]:
        return {
            "type": _get_command_type(self),
            "args": _get_command_args(self),
        }


@dataclass
class GetPortfolio(Command):
    portfolio_id: str


@dataclass
class CreatePortfolio(Command):
    name: str
    assets: dict[str, float]


@dataclass
class ListPortfolios(Command):
    pass


def _get_command_type(cmd: Command) -> str:
    return cmd.__class__.__name__


def _get_command_args(cmd: Command) -> dict[str, T.Any]:
    return asdict(cmd) 
