"""Module for custom exceptions used in the stega core service."""


class CoreAppError(Exception):
    """Base class for all core application errors."""


class ConflictError(CoreAppError):
    """Exception raised when there is a conflict in the core service."""


class ResourceNotFoundError(CoreAppError):
    """Exception raised when a requested resource is not found in the core service."""
