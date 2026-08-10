from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    cfrom collections.abc import AsyncIterator


@dataclass
class ServerSentEvent:
    data: str
    event: str | None = None
    sse_id: int | None = None
    retry: int | None = None

    def encode(self) -> bytes:
        lines = []
        if self.event is not None:
            lines.append(f"event: {self.event}")
        if self.sse_id is not None:
            lines.append(f"id: {self.sse_id}")
        if self.retry is not None:
            lines.append(f"retry: {self.retry}")
        lines.append(f"data: {self.data}")
        return ("\n".join(lines) + "\n\n").encode("utf-8") 


async def decode(lines: AsyncIterator[str]) -> AsyncIterator[ServerSentEvent]:
    event: str | None = None
    sse_id: int | None = None
    retry: int | None = None
    data: list[str] = []
    async for line in lines:
        if line == "":
            if data:
                yield ServerSentEvent(data="\n".join(data), event=event, sse_id=sse_id, retry=retry)
            event, sse_id, retry, data = None, None, None, []
            continue
        if line.startswith(":"):
            continue
        field, _, value = line.partition(":")
        if value.startswith(" "):
            value = value[1:]
        if field == "data":
            data.append(value)
        elif field == "event":
            event = value
        elif field == "id":
            sse_id = int(value)
        elif field == "retry":
            retry = int(value)
    if data:
        yield ServerSentEvent(data="\n".join(data), event=event, sse_id=sse_id, retry=retry)
