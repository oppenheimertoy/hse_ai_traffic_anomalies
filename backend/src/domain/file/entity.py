import uuid
from dataclasses import dataclass

from src.domain.entity import BaseEntity


@dataclass
class File(BaseEntity):
    created_by: uuid.UUID
    file_url: str
    file: bytes | None = None