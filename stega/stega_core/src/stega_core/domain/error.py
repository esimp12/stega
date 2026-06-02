class AppError(Exception):
    """Base class for all service errors."""


class ConflictError(AppError):
    """Exception raised when there is a conflict in the service."""


class ResourceNotFoundError(AppError):
    """Exception raised when a requested resource is not found in the service."""
