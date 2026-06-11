

class HttpChannel(Channel):

    def __init__(
        self,
        base_url: str,
        routes: dict[type[Message], Route],
    ) -> None:
        self._base_url = base_url
        self.routes = routes
        self.session: aiohttp.ClientSession | None = None

    async def open(self) -> None:
        self.session = aiohttp.ClientSession(base_url=self._base_url)

    async def close(self) -> None:
        if self.session is not None:
            await self.session.close()
            self.session = None


class HttpTransport(AbstractTransport[HttpChannel]):

    async def dispatch(self, message: Message) -> ServiceResult:
        route = self._channel.routes[type(message)]
        path, headers, payload = self._render(route, message)
        kwargs = {
            "headers": headers,
            "params" if route.method == "GET" else "json": payload,
        }
        async with self._channel.session.request(route.method, path, **kwargs) as resp:
            data = await.json()
        return ServiceResult(
            ok=data["ok"],
            msg=data["msg"],
            result=data["result"],
        )

    def _render(self, route: Route, message: Message):
        ...
