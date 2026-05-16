
from sqlalchemy.ext.asnyncio import AsyncSession

from stega_core.reader.base import AbstractReader


class AbstractSqlAlchemyReader(AbstractReader):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self._session = session
