"""Module for custom exceptions used in the stega portfolio service."""


class PortfolioAppError(Exception):
    """Base class for all portfolio application errors."""


class ConflictError(PortfolioAppError):
    """Exception raised when there is a conflict in the portfolio service."""


class ResourceNotFoundError(PortfolioAppError):
    """Exception raised when a requested resource is not found in the portfolio service."""
