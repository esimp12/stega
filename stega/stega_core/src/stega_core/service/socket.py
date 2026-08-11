from __future__ import annotations

import asyncio
import json
import struct
from dataclasses import asdict
from typing import TYPE_CHECKING, Any

from stega_core.service.channel import Channel
from stega_core.service.transport import AbstractTransport, ServiceResult

if TYPE_CHECKING:
    from stega_core.message import Message

_HEADER = struct.Struct("!I")


async def write_frame(writer: asyncio.StreamWriter, data: dict[str, Any]) -> None:
    payload = json.dumps(data).encode("utf-8")
    writer.write(_HEADER.pack(len(payload)) + payload)
    await writer.drain()


async def read_frame(reader: asyncio.StreamReader) -> dict[str, Any]:
    (length,) = _HEADER.unpack(await reader.readexactly(_HEADER.size))
    payload = await reader.readexactly(length)
    return json.loads(payload.decode("utf-8"))


class UnixSocketChannel(Channel):
    def __init__(self, socket_path: str) -> None:
        self._socket_path = socket_path
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None

    async def open(self) -> None:
        self.reader, self.writer = await asyncio.open_unix_connection(self._socket_path)

    async def close(self) -> None:
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        self.reader = None
        self.writer = None


class UnixSocketTransport(AbstractTransport[UnixSocketChannel]):
    async def dispatch(self, message: Message) -> ServiceResult:
        await write_frame(
            self._channel.writer,
            {"msg_type": type(message).__name__, "payload": asdict(message)},
        )
        data = await read_frame(self._channel.reader)
        return ServiceResult(
            ok=data["ok"],
            msg=data["msg"],
            result=data["result"],
        )
