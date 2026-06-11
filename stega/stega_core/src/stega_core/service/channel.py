from abc import ABC


class Channel(ABC):

    async def open(self) -> None:
        ...

    async def close(self) -> None:
        ...
