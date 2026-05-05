import json
from collections.abc import AsyncIterator
from dataclasses import dataclass

import aio_pika

from stega_lib.transport.base import MessageTransport, TransportMessage


@dataclass(frozen=True, kw_only=True)
class RabbitMqConnectionParameters:
    host: str
    port: int
    username: str
    password: str


class RabbitMqTransport(MessageTransport):

    def __init__(
        self,
        connection_params: RabbitMqConnectionParameters,
        exchange_name: str,
    ) -> None:
        self._connection_params = connection_params
        self._exchange_name = exchange_name

        self._connection: aio_pika.abc.AbstractConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None
        self._exchange: aio_pika.abc.AbstractExchange | None = None

    async def start(self) -> None:
        self._connection = await aio_pika.connect(
            host=self._connection_params.host,
            port=self._connection_params.port,
            login=self._connection_params.username,
            password=self._connection_params.password,
        )
        self._channel = await self._connection.channel()
        self._exchange = await self._channel.declare_exchange(
            self._exchange_name,
            aio_pika.ExchangeType.DIRECT,
            durable=True,
        )

    async def stop(self) -> None:
        if self._channel is not None:
            await self._channel.close()
            self._channel = None
        if self._connection is not None:
            await self._connection.close()
            self._connection = None
        self._exchange = None

    async def publish(self, message: TransportMessage) -> None:
        if self._exchange is None:
            raise RuntimeError("Transport not started")
        body = json.dumps(message.body).encode()
        await self._exchange.publish(
            aio_pika.Message(body=body, content_type="application/json"),
            routing_key=message.topic,
        )

    async def subscribe(self, topics: list[str]) -> AsyncIterator[TransportMessage]:
        if self._channel is None or self._exchange is None:
            raise RuntimeError("Transport not started")

        queue = await self._channel.declare_queue(
            name="",
            exclusive=True,
            auto_delete=True,
            durable=False,
        )
        for topic in topics:
            await queue.bind(self._exchange, routing_key=topic)

        async with queue.iterator(no_ack=True) as consumer:
            async for rabbit_msg in consumer:
                async with rabbit_msg.process(requeue=True):
                    body = json.loads(rabbit_msg.body.decode())
                    yield TransportMessage(
                        topic=rabbit_msg.routing_key or "",
                        body=body,
                    )
