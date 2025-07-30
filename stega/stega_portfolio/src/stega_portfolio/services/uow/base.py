"""Resource manager for handling atomic service transactions."""

import abc
import types
import typing as T

from stega_lib.events import Event

from stega_portfolio.ports.repos.base import AbstractPortfolioRepository


class AbstractUnitOfWork(abc.ABC):
    """Abstract base class for atomic service transactions.

    A unit of work is intended to manage any resources needed for accessing external
    systems. Concrete units of work are responsible for acquiring and releasing any
    technology specific resources in its context.
    """

    portfolios: AbstractPortfolioRepository

    def __enter__(self) -> T.Self:
        """Handle the opening of an atomic service transaction.

        Any resources that need to be acquired or opened should likely occur here.

        Returns:
            A self reference to the given AbstractUnitOfWork.

        """
        return self

    def __exit__(
        self,
        _type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        """Handle the closing of an atomic service transaction.

        Any resources that need to be release or closed should likely occur here.

        If a caller fails to commit the work in the given context, then any
        transactions performed in this context will not take place by default - the
        work will be rolled back.

        NOTE: The _type, exc, and traceback parameters are currently unused.

        Args:
            _type: The type of exception raised, if any.
            exc: The exception raised, if any.
            traceback: The traceback of the exception raised, if any.

        """
        self.rollback()

    def collect_new_events(self) -> T.Generator[Event, None, None]:
        """Collect any new events that have been generated in the unit of work.

        Yields:
            The latest event that has been generated in the unit of work.

        """
        for portfolio in self.portfolios.seen:
            while portfolio.events:
                yield portfolio.events.pop(0)

    @abc.abstractmethod
    def commit(self) -> None:
        """Guarantees transactions will be honored when the unit of work exits."""
        err_msg = "Commit method not implemented."
        raise NotImplementedError(err_msg)

    @abc.abstractmethod
    def rollback(self) -> None:
        """Reverts any transactions declared in the given context."""
        err_msg = "Rollback method not implemented."
        raise NotImplementedError(err_msg)
