from stega_core.bus import MessageBus
from stega_core.message import Command, Message, Query
from stega_core.service.channel import Channel
from stega_core.service.transport import AbstractTransport, ServiceResult


class InMemoryChannel(Channel):

    def __init__(self, bus: MessageBus) -> None:
        self.bus = bus

class InMemoryTransport(AbstractTransport[InMemoryChannel]):

    async def dispatch(self, message: Message) -> ServiceResult:
        bus = self._channel.bus
        if isinstance(message, Command):
            resp = await bus.handle_command(message)
        elif isinstance(message, Query):
            resp = await bud.handle_query(message)
        return ServiceResult(resp.ok, msg="", result=resp.result)
