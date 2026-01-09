from src.domain.errors import DomainError


class FileUploadError(DomainError):
    def __init__(self, message: str = "Error while uploading file"):
        super().__init__(message)


class FileDownloadError(DomainError):
    def __init__(self, message: str = "Error while download file"):
        super().__init__(message)
