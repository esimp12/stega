import asyncio

import uuid_utils as uuid

from stega_cli.domain.command import (
    Command,
    CreatePortfolio,
    GetPortfolio,
    ListPortfolios,
    ReadCommand,
    WriteCommand,
)
from stega_cli.domain.request import (
    CommandRequest,
    CreatePortfolioRequest,
    GetPortfolioRequest,
    ListPortfoliosRequest,
    ReadCommandRequest,
    Response,
    WriteCommandRequest,
)
from stega_cli.services.command import CommandDispatcher

CommandRequestType = type[CommandRequest]
CommandType = type[Command]
RequestCommandMapping = dict[CommandRequestType, CommandType]

_REQUEST_COMMAND_MAPPING: RequestCommandMapping = {
    CreatePortfolioRequest: CreatePortfolio,
    GetPortfolioRequest: GetPortfolio,
    ListPortfoliosRequest: ListPortfolios,
}


class RequestDispatcher:
    """Dispatch command requests to the corresponding service command.

    This takes a generic CommandRequest instance and determines if the
    requested work involves 'reads' or 'writes'. If it involves reads then
    a consumeable response is expected and synchronous work may occur in the
    callee. Otherwise, an immediate response with a correlation id is expected
    with some indication that the request for work was accepted. The
    correlation id may be used to track the requested work throughout the
    system. Both return paths wrap their results in a Response instance so
    callers can write abstract message handling code.

    """

    def __init__(
        self,
        cmd_dispatcher: CommandDispatcher,
        cmd_queue: asyncio.Queue,
    ) -> None:
        self._cmd_dispatcher = cmd_dispatcher
        self._cmd_queue = cmd_queue

    async def handle(self, cmd_request: CommandRequest) -> Response:
        """Route an incoming CommandRequest to the approriate type.

        Args:
            cmd_request: A CommandRequest instance to dispatch.

        Returns:
            A Response instance of the result of the request.

        Raises:
            A ValueError if the incoming CommandRequest is not a valid read
            or write request.

        """
        if isinstance(cmd_request, ReadCommandRequest):
            cmd = gen_read_cmd(cmd_request)
            return self._cmd_dispatcher.handle(cmd)
        if isinstance(cmd_request, WriteCommandRequest):
            cmd = gen_write_cmd(cmd_request)
            await self._cmd_queue.put(cmd)
            return Response(
                status="ok",
                result={"correlation_id": cmd.correlation_id},
            )
        err_msg = f"'{type(cmd_request)}' is not a recognized CommandRequest type."
        raise ValueError(err_msg)


def gen_read_cmd(cmd_request: ReadCommandRequest) -> ReadCommand:
    """Generate the corresponding ReadCommand from a ReadCommandRequest.

    Args:
        cmd_request: A ReadCommandRequest instance.

    Returns:
        A ReadCommand instance.

    """
    cmd_type = _REQUEST_COMMAND_MAPPING[type(cmd_request)]
    return cmd_type(**cmd_request.args)


def gen_write_cmd(cmd_request: WriteCommandRequest) -> WriteCommand:
    """Generate the corresponding WriteCommand from a WriteCommandRequest.

    Args:
        cmd_request: A WriteCommandRequest instance.

    Returns:
        A WriteCommand instance.

    """
    cmd_type = _REQUEST_COMMAND_MAPPING[type(cmd_request)]
    kwargs = {
        "correlation_id": gen_correlation_id(),
        **cmd_request.args,
    }
    return cmd_type(**kwargs)


def gen_correlation_id() -> str:
    """Generate a new globally unique correlation ID.

    Returns:
        A str of the globally unique ID used for system event tracing.

    """
    return str(uuid.uuid7())
