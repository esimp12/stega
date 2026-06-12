import functools
import json
import logging
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, TypedDict

from quart import Quart, Request, Response, current_app, make_response, request

from stega_core.bootstrap import Service
from stega_core.bus import MessageBus
from stega_core.context import current_context, set_context
from stega_core.domain import (
    AppError,
    ConflictError,
    ResourceNotFoundError,
)
from stega_core.hosting.marshal import marshal
from stega_core.message import Command, Message, MessageResponse, Query


class Wire(StrEnum):
    BODY = "body"
    QUERY = "query"
    PATH = "path"
    HEADER = "header"


class Origin(StrEnum):
    MESSAGE = "message"
    CONTEXT = "context"


@dataclass(frozen=True, kw_only=True)
class Binding:
    key: str
    wire: Wire
    origin: Origin = Origin.MESSAGE
    wire_key: str | None = None

    @property
    def name(self) -> str:
        return self.wire_key or self.key


class ResponsePayload(TypedDict):
    ok: bool
    msg: str
    result: Any


type AppResponse = tuple[ResponsePayload, int]


@dataclass(frozen=True, kw_only=True)
class Route:
    method: str
    path: str
    msg_type: type[Message]
    msg_callback: Callable[[MessageResponse], str]
    prefix: str | None = None
    bindings: list[Binding] = field(default_factory=list)


@dataclass(frozen=True, kw_only=True)
class SseRoute:
    path: str
    prefix: str | None = None


@dataclass
class ServerSentEvent:
    data: str
    event: str | None = None
    sse_id: int | None = None
    retry: int | None = None

    def encode(self) -> bytes:
        message = f"data: {self.data}"
        if self.event is not None:
            message = f"{message}\nevent: {self.event}"
        if self.sse_id is not None:
            message = f"{message}\nid: {self.sse_id}"
        if self.retry is not None:
            message = f"{message}\nretry: {self.retry}"
        return message.encode("utf-8")


async def deserialize(route: Route, request: Request) -> tuple[Message, dict[str, Any]]:
    body = {}
    if request.is_json:
        body = await request.get_json()
    raw: dict = {**body, **request.args.to_dict(), **request.view_args}
    ctx: dict = {}
    readers = {
        Wire.HEADER: request.headers.get,
        Wire.QUERY: request.args.get,
        Wire.PATH: request.view_args.get,
        Wire.BODY: body.get,
    }
    for b in route.bindings:
        val = readers[b.wire](b.name)
        if val is None:
            continue
        if b.origin is Origin.CONTEXT:
            ctx[b.key] = val
            raw.pop(b.key, None)
        else:
            raw[b.key] = val
    return marshal(route.msg_type, raw), ctx


def get_service() -> Service:
    return current_app.extensions["service"]


def get_bus() -> MessageBus:
    return get_service().bus


def make_app_response(
    ok: bool,  # noqa: FBT001
    msg: str,
    result: Any,  # noqa: ANN401
    return_code: int,
) -> AppResponse:
    return {
        "ok": ok,
        "msg": msg,
        "result": result,
    }, return_code


async def handle_request(
    route: Route,
    **_: Any,  # noqa: ANN401
) -> AppResponse:
    # deserialize raw request into message and context vars
    message, ctxvars = await deserialize(route, request)

    # set request context based on requested route contextvars
    if ctxvars:
        ctx = current_context()
        for ctxkey, ctxval in ctxvars.items():
            ctx[ctxkey] = ctxval
        set_context(ctx)

    # handle message on bus
    bus = get_bus()
    if isinstance(message, Command):
        resp = await bus.handle_command(message)
        result = None
        return_code = 201
    if isinstance(message, Query):
        resp = await bus.handle_query(message)
        result = resp.result
        return_code = 200

    if resp is None:
        err_msg = f"{type(message)} is not a valid message type for a request to handle"
        raise AppError(err_msg)

    if not resp.ok:
        raise AppError(resp.error)

    return make_app_response(resp.ok, route.msg_callback(resp), result, return_code)


def app_exception_handler(exc: Exception, logger: logging.Logger) -> AppResponse:
    return_code = 500
    if isinstance(exc, ConflictError):
        return_code = 409
    elif isinstance(exc, ResourceNotFoundError):
        return_code = 404
    elif isinstance(exc, AppError):
        return_code = 400

    exc_info = (type(exc), exc, exc.__traceback__)
    logger.exception(exc, exc_info=exc_info)
    return make_app_response(
        ok=False,
        msg=str(exc),
        result=None,
        return_code=return_code,
    )


def make_sse_handler() -> Callable[..., Awaitable[Response]]:
    async def handle_sse(
        topic: str,
        **_: Any,  # noqa: ANN401
    ) -> Response:
        service = get_service()
        if topic not in service.bus.subscribed_topics:
            return make_app_response(
                ok=False,
                msg=f"No topic found for '{topic}'!",
                result=None,
                return_code=400,
            )

        client_broker = service.client_broker

        async def send_events() -> AsyncIterator[bytes]:
            async for envelope in client_broker.subscribe(topic):
                event = ServerSentEvent(
                    data=json.dumps(envelope.payload),
                    event=envelope.topic,
                )
                yield event.encode()

        headers = {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Transfer-Encoding": "chunked",
        }
        response = await make_response(send_events(), headers)
        response.timeout = None
        return response

    return handle_sse


def build_quart_app(
    service: Service,
    routes: list[Route],
    sse_routes: list[SseRoute] | None = None,
) -> Quart:
    if sse_routes is None:
        sse_routes = []

    app = Quart(__name__)

    # setup service lifespan
    app.extensions = getattr(app, "extensions", {})

    @app.while_serving
    async def _manage_service() -> Awaitable[None]:
        async with service.lifespan():
            app.extensions["service"] = service
            try:
                yield
            finally:
                app.extensions.pop("service", None)

    # register routes
    for route in routes:
        handler = functools.partial(
            handle_request,
            route=route,
        )
        rule = route.path if route.prefix is None else f"{route.prefix}{route.path}"
        app.add_url_rule(
            rule=rule,
            endpoint=f"<{route.method} {rule}>",
            view_func=handler,
            methods=[route.method],
        )

    # register sse routes
    for sse_route in sse_routes:
        handler = make_sse_handler()
        rule = sse_route.path if sse_route.prefix is None else f"{sse_route.prefix}{sse_route.path}"
        app.add_url_rule(
            rule=rule,
            endpoint=f"<SSE GET {rule}>",
            view_func=handler,
            methods=["GET"],
        )

    # add health route
    @app.route("/api/health", methods=["GET"])
    async def health() -> AppResponse:
        return make_app_response(
            ok=True,
            msg="Service is healthy!",
            result=None,
            return_code=200,
        )

    # add favicon.ico route
    @app.route("/favicon.ico", methods=["GET"])
    async def favicon() -> tuple[str, int]:
        return "", 204

    # register error handlers
    exc_handler = functools.partial(app_exception_handler, logger=service.logger)
    app.register_error_handler(Exception, exc_handler)

    return app
