import uuid

from src.domain.dto import BaseDTO


class FileCreateDTO(BaseDTO): 
    file: bytes
    user_id: uuid.UUID
    file_url: str | None = None
