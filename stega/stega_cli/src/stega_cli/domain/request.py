import sys
from dataclasses import dataclass, asdict
import typing as T


@dataclass
class Response:
    """Response to send ack back from CLI daemon."""

    status: str
    result: dict[str, T.Any]

    def to_dict(self) -> dict[str, T.Any]:
        return {
            "status": self.status,
            "result": self.result,
        }


@dataclass
class CommandRequest:
    """CommandRequest to send to CLI daemon."""

    @property
    def args(self) -> dict[str, T.Any]:
        return _get_command_args(self)
    
    def to_dict(self) -> dict[str, T.Any]:
        return {
            "type": _get_command_type(self),
            "args": self.args,
        }

    @classmethod
    def from_dict(cls, cmd_dict: dict[str, T.Any]) -> CommandRequest:
        class_str = cmd_dict["type"] 
        klass = _get_command_class(class_str)
        kwargs = cmd_dict["args"]
        return klass(**kwargs)


@dataclass
class ReadCommandRequest(CommandRequest):
    pass


@dataclass
class WriteCommandRequest(CommandRequest):
    pass


@dataclass
class GetPortfolio(ReadCommandRequest):
    portfolio_id: str


@dataclass
class CreatePortfolio(WriteCommandRequest):
    name: str
    assets: dict[str, float]


@dataclass
class ListPortfolios(ReadCommandRequest):
    pass


def _get_command_type(cmd: Command) -> str:
    return cmd.__class__.__name__


def _get_command_args(cmd: Command) -> dict[str, T.Any]:
    return asdict(cmd) 


def _get_command_class(klass_str: str) -> type:
    module = sys.modules[__name__]
    return getattr(module, klass_str)

