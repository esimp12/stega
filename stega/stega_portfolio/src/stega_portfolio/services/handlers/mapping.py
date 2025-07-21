"""Service handler mapping for stega_portfolio."""

import typing as T

from stega_lib.domain import Command

from stega_portfolio.domain.commands import CreatePortfolio
from stega_portfolio.services.handlers.portfolio import create_portfolio

CommandType = type[Command]


COMMAND_HANDLERS: T.Mapping[CommandType, T.Callable] = {
    CreatePortfolio: create_portfolio,
}
