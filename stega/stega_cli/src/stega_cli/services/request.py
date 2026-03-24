import asyncio

import uuid_utils as uuid

from stega_cli.services.command import CommandDispatcher
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
    WriteCommandRequest,
    Response,
)


CommandRequestType = type[CommandRequest]
CommandType = type[Command]
RequestCommandMapping = dict[CommandRequestType, CommandType]

_REQUEST_COMMAND_MAPPING: RequestCommandMapping = {
    CreatePortfolioRequest: CreatePortfolio,
    GetPortfolioRequest: GetPortfolio,
    ListPortfoliosRequest: ListPortfolios,
}


class RequestDispatcher:

    def __init__(
        self,
        cmd_dispatcher: CommandDispatcher,
        cmd_queue: asyncio.Queue,
    ) -> None:
        self._cmd_dispatcher = cmd_dispatcher
        self._cmd_queue = cmd_queue

    async def handle(self, cmd_request: CommandRequest) -> Response:
        if isinstance(cmd_request, ReadCommandRequest):
            cmd = gen_read_cmd(cmd_request)
            return self._cmd_dispatcher.handle(cmd)
        elif isinstance(cmd_request, WriteCommandRequest):
            cmd = gen_write_cmd(cmd_request)
            await self._cmd_queue.put(cmd)
            return Response(
                status="ok",
                result={"correlation_id": cmd.correlation_id}
            )


def gen_read_cmd(cmd_request: ReadCommandRequest) -> ReadCommand:
    cmd_type = _REQUEST_COMMAND_MAPPING[type(cmd_request)]
    return cmd_type(**cmd_request.args)


def gen_write_cmd(cmd_request: WriteCommandRequest) -> WriteCommand:
    cmd_type = _REQUEST_COMMAND_MAPPING[type(cmd_request)]
    kwargs = {
        "correlation_id": gen_correlation_id(),
        **cmd_request.args,
    }
    return cmd_type(**kwargs)


def gen_correlation_id() -> str:
    return str(uuid.uuid7())

