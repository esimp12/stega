from __future__ import annotations

import sys
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class Response:
    """Response to send ack back from CLI daemon.

    Attributes:
        status: A str of the state of the response.
        result: A dict of the actual response contents.

    """

    status: str
    result: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert the response to a serializeable dict.

        Returns:
            A dict of the response.

        """
        return {"status": self.status, "result": self.result}


@dataclass
class CommandRequest:
    """Command request to send to CLI daemon."""

    @property
    def args(self) -> dict[str, Any]:
        """Get the command args supplied to the command request.

        Returns:
            A dict of the command args.

        """
        return _get_command_args(self)

    def to_dict(self) -> dict[str, Any]:
        """Convert the command request to a serializeable dict.

        Returns:
            A dict of the command request.

        """
        return {"type": _get_command_type(self), "args": self.args}

    @classmethod
    def from_dict(cls, cmd_dict: dict[str, Any]) -> CommandRequest:
        """Create a CommandRequest instance from a dict of properties.

        Args:
            cmd_dict: A dict of the instance properties to create a
                CommandRequest.

        Returns:
            A CommandRequest instance with the given properties.

        """
        class_str = cmd_dict["type"]
        klass = _get_command_class(class_str)
        kwargs = cmd_dict["args"]
        return klass(**kwargs)


@dataclass
class ReadCommandRequest(CommandRequest):
    """Command request for read actions."""


@dataclass
class WriteCommandRequest(CommandRequest):
    """Command request for write actions."""


@dataclass
class GetPortfolioRequest(ReadCommandRequest):
    """Command request for fetching a portfolio.

    Attributes:
        portfolio_id: A str of the unique ID of the portfolio.

    """

    portfolio_id: str


@dataclass
class CreatePortfolioRequest(WriteCommandRequest):
    """Command request for creating a new portfolio.

    Attributes:
        name: A str of the portfolio name.
        assets: A list of portfolio assets as dict instances. An asset contains
            both a symbol and a weight.

    """

    name: str
    assets: dict[str, float]


@dataclass
class ListPortfoliosRequest(ReadCommandRequest):
    """Command request for listing portfolios."""


def _get_command_type(cmd: CommandRequest) -> str:
    return cmd.__class__.__name__


def _get_command_args(cmd: CommandRequest) -> dict[str, Any]:
    return asdict(cmd)


def _get_command_class(klass_str: str) -> type:
    module = sys.modules[__name__]
    return getattr(module, klass_str)
