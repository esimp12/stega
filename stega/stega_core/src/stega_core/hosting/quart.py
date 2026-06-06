import functools
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any, TypedDict

from quart import Quart, Request, current_app, request

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
    translation: dict[str, str] = field(default_factory=dict)
    contextvars: set[str] = field(default_factory=set)


async def merge_request(request: Request, translation: dict[str, str]) -> dict[str, Any]:
    raw: dict[str, Any] = {}
    if request.is_json:
        raw |= await request.get_json()
    raw |= request.args.to_dict()
    raw |= request.view_args
    for source_key, translated_key in translation.items():
        if source_key in request.headers:
            raw[translated_key] = request.headers[source_key]
    return raw


def get_bus() -> MessageBus:
    service = current_app.extensions["service"]
    return service.bus


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
    # parse raw envelope of request
    raw = await merge_request(request, route.translation)
    
    # set request context based on requested route contextvars
    if route.contextvars:
        ctx = current_context()
        for var in route.contextvars:
            ctx[var] = raw.get(var)
        set_context(ctx)

    # create concrete Command message and handle on bus
    message = marshal(route.msg_type, raw)
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


def build_quart_app(service: Service, routes: list[Route]) -> Quart:
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
        rule = f"{route.path}" if route.prefix is None else f"{route.prefix}{route.path}"
        app.add_url_rule(
            rule=rule,
            endpoint=f"<{route.method} {rule}>",
            view_func=handler,
            methods=[route.method],
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
