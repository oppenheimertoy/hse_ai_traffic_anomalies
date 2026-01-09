from src.domain.errors import DomainError


class FileProcessingError(DomainError):
    def __init__(self, message: str = ""):
        super().__init__(f"file processing error: {message}")


class StatusUpdateError(DomainError):
    def __init__(self, message: str = ""):
        super().__init__(f"Status update error: {message}")
