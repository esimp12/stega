from __future__ import annotations

import asyncio
import functools
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING

from stega_core import marshal, read_frame, write_frame

from stega_cli.bootstrap import build_edge_port
from stega_cli.commands import MESSAGE_TYPES
from stega_cli.daemon.dispatch import RequestDispatcher
from stega_cli.daemon.handlers import SUBSCRIPTIONS
from stega_cli.daemon.tail import run_tail
from stega_cli.daemon.worker import run_writer
from stega_cli.ports.cache import db

if TYPE_CHECKING:
    from stega_cli.config import CliConfig


async def handle_client(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter,
    dispatcher: RequestDispatcher,
) -> None:
    try:
        frame = await read_frame(reader)
        msg_type = MESSAGE_TYPES[frame["msg_type"]]
        result = await dispatcher.handle(marshal(msg_type, frame["payload"]))
        response = {"ok": result.ok, "msg": result.msg, "result": result.result}
    except Exception as exc:
        response = {"ok": False, "msg": f"{type(exc).__name__}: {exc}", "result": None}
    try:
        await write_frame(writer, response)
    finally:
        writer.close()
        with suppress(ConnectionError):
            await writer.wait_closed()


def prepare(config: CliConfig) -> None:
    db.init_db(config.db_path)
    Path(config.socket_path).unlink(missing_ok=True)


async def serve(config: CliConfig) -> None:
    queue: asyncio.Queue = asyncio.Queue()
    port_factory = functools.partial(build_edge_port, config)
    dispatcher = RequestDispatcher(port_factory, queue, config.db_path)

    server = await asyncio.start_unix_server(
        functools.partial(handle_client, dispatcher=dispatcher),
        path=str(config.socket_path),
    )

    async with asyncio.TaskGroup() as tasks:
        tasks.create_task(server.serve_forever())
        tasks.create_task(run_writer(queue, port_factory))
        for event_type in SUBSCRIPTIONS:
            tasks.create_task(run_tail(config, event_type.topic))
