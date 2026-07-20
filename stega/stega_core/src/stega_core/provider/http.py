import httpx

from stega_utils.limiter import RateLimiterStack


class HttpProviderChannel:

    def __init__(
        self,
        base_url: str,
        *,
        http2: bool = True,
        limits: httpx.Limits | None = None,
        limiters: RateLimiterStack | None = None,
    ) -> None:
        self._base_url = base_url
        self._http2 = http2
        self._limits = limits
        self._limiters = limiters if limiters is not None else RateLimiterStack([])
        self._client: httpx.AsyncClient | None = None

    async def start(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            http2=self._http2,
            limits=self._limits,
        )

    async def stop(self) -> None:
        if self._client is not None:
            await self._client.aclose()

    async def get(self, path: str, params: dict | None = None) -> httpx.Response:
        async with self._limiters:
            return await self._client.get(path, params=params)
    
    async def get_unmetered(self, path: str, params: dict | None = None) -> httpx.Response:
        return await self._client.get(path, params=params)
