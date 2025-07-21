"""Manages acquiring and releasing of SQL database connection sessions."""

import types
import typing as T

from sqlalchemy.orm import Session

from stega_portfolio.ports.repos.db import SqlAlchemyPortfolioRepository
from stega_portfolio.services.uow.base import AbstractUnitOfWork


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """Manages Session resources for executing SQL commands.

    Attributes:
        session_factory: A Callable that returns a new SQLAlchemy Session when called.
        session: A SQLAlchemy Session to connect to a SQL database.

    """

    def __init__(self, session_factory: T.Callable[[], Session]) -> None:
        """Initialize the SqlAlchemyUnitOfWork with a session factory."""
        self.session = None
        self.session_factory = session_factory

    def __enter__(self) -> T.Self:
        """Create a new database connection."""
        self.session = self.session_factory()
        self.portfolios = SqlAlchemyPortfolioRepository(self.session)
        return super().__enter__()

    def __exit__(
        self,
        _type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        """Close the existing database connection."""
        super().__exit__(_type, exc, traceback)
        if self.session is not None:
            self.session.close()

    def commit(self) -> None:
        """See AbstractUnitOfWork."""
        if self.session is not None:
            self.session.commit()

    def rollback(self) -> None:
        """See AbstractUnitOfWork."""
        if self.session is not None:
            self.session.rollback()
