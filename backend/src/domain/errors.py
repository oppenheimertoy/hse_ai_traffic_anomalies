class DomainError(Exception):
    """Base exception for domain-level errors."""

    status_code: int = 400


class NotFoundError(DomainError):
    """Raised when an entity cannot be located."""

    status_code = 404


class IntegrityError(DomainError):
    """Raised when a constraint violation occurs."""

    status_code = 409
