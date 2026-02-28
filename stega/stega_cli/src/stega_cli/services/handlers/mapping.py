import typing as T

from stega_cli.domain.command import (
    Command,
    GetPortfolio,
    CreatePortfolio,
)
from stega_cli.domain.request import Response
from stega_cli.services.handlers.portfolio import get_portfolio, create_portfolio


CommandType = type[Command]
CommandHandlerType = T.Callable[[Command], T.Optional[Response]]
CommandHandlers = dict[CommandType, CommandHandlerType]

COMMAND_HANDLERS: CommandHandlers = {
    GetPortfolio: get_portfolio,
    CreatePortfolio: create_portfolio,
}

