from src.domain.errors import DomainError


class UserExistsError(DomainError):
    status_code = 409

    def __init__(self, message: str = "User already exists") -> None:
        super().__init__(message)


class UserNotFoundError(DomainError):
    status_code = 404

    def __init__(self, message: str = "User not found") -> None:
        super().__init__(message)


class UserValidationError(DomainError):
    status_code = 401

    def __init__(self, message: str = "Invalid username or password") -> None:
        super().__init__(message)
