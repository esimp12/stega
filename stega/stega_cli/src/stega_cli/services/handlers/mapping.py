import typing as T

from stega_cli.domain.command import Command, CreatePortfolio, GetPortfolio, ListPortfolios
from stega_cli.domain.request import Response
from stega_cli.services.handlers.portfolio import (
    create_portfolio,
    get_portfolio,
    list_portfolios,
)

CommandType = type[Command]
CommandHandlerType = T.Callable[[Command], Response | None]
CommandHandlers = dict[CommandType, CommandHandlerType]

COMMAND_HANDLERS: CommandHandlers = {
    GetPortfolio: get_portfolio,
    CreatePortfolio: create_portfolio,
    ListPortfolios: list_portfolios,
}

