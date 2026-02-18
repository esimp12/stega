import typig as T

from stega_cli.domain.command import Response, Command, GetPortfolio
from stega_cli.services.handlers.portfolio import get_portfolio, create_portfolio


CommandType = type[Command]
ResponseType = type[Response]
CommandHandlerType = T.Callable[[Command], ResponseType]

COMMAND_HANDLERS: dict[CommandType, CommandHandlerType] = {
    GetPortfolio: get_portfolio,
    CreatePortfolio: create_portfolio,
}

