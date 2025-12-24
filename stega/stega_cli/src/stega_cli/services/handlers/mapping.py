import typig as T

from stega_cli.domain.command import Response, Command, GetPortfolio


CommandType = type[Command]
ResponseType = type[Response]
CommandHandlerType = T.Callable[[Command], ResponseType]

COMMAND_HANDLERS: dict[CommandType, CommandHandlerType] = {
    GetPortfolio: ,
}

