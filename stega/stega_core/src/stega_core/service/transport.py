from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from stega_core.service.channel import Channel

if TYPE_CHECKING:
    from stega_core.message import Message


@dataclass(frozen=True, kw_only=True)
class ServiceResult:
    ok: bool
    msg: str
    result: Any


class AbstractTransport[ChannelT: Channel](ABC):
    def __init__(self, channel: ChannelT) -> None:
        self._channel = channel

    @abstractmethod
    async def dispatch(self, message: Message) -> ServiceResult: ...
