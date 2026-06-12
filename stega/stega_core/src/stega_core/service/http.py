import re
from dataclasses import asdict
from typing import Any

import httpx

from stega_core.context import current_context
from stega_core.hosting import Origin, Route, Wire
from stega_core.message import Message
from stega_core.service.channel import Channel
from stega_core.service.transport import AbstractTransport, ServiceResult

_PATH_PARAM = re.compile(r"<(?:[^:<>]+:)?([^<>]+)>")


class HttpChannel(Channel):
    def __init__(
        self,
        base_url: str,
        routes: dict[type[Message], Route],
    ) -> None:
        self._base_url = base_url
        self.routes = routes
        self.session: httpx.AsyncClient | None = None

    async def open(self) -> None:
        self.session = httpx.AsyncClient(base_url=self._base_url)

    async def close(self) -> None:
        if self.session is not None:
            await self.session.close()
            self.session = None


class HttpTransport(AbstractTransport[HttpChannel]):
    async def dispatch(self, message: Message) -> ServiceResult:
        route = self._channel.routes[type(message)]
        path, headers, params, body = self._render(route, message, current_context())
        kwargs = {}
        if headers:
            kwargs["headers"] = headers
        if params:
            kwargs["params"] = params
        if body:
            kwargs["json"] = body
        async with self._channel.session() as client:
            request = client.build_request(route.method, path, **kwargs)
            resp = await client.send(request)
            data = resp.json()
        return ServiceResult(
            ok=data["ok"],
            msg=data["msg"],
            result=data["result"],
        )

    def _render(self, route: Route, message: Message, ctx: dict[str, Any]) -> tuple[str, dict, dict, dict]:
        fields = asdict(message)
        headers, params, body = {}, {}, {}
        sinks = {
            Wire.HEADER: headers,
            Wire.QUERY: params,
            Wire.BODY: body,
        }

        for b in route.bindings:
            src = ctx if b.origin is Origin.CONTEXT else fields
            if b.key not in src:
                continue
            val = src[b.key]
            sinks[b.wire][b.name] = str(val) if b.wire is Wire.HEADER else val
            if b.origin is Origin.MESSAGE:
                fields.pop(b.key, None)

        consumed: list[str] = []

        def _sub(m: re.Match) -> str:
            consumed.append(m.group(1))
            return str(fields[m.group(1)])

        path = _PATH_PARAM.sub(_sub, route.path)
        for name in consumed:
            fields.pop(name, None)
        if route.prefix:
            path = f"{route.prefix}{path}"

        if route.method == "GET":
            params.update(fields)
        else:
            body.update(fields)
        return path, headers, params, body
