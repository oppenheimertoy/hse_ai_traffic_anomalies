import uuid

import src.domain.file.entity as file_entity
from src.domain.dto import BaseDTO
from src.domain.history.entity import HistoryStatus


class HistoryCreateDTO(BaseDTO):
    file_url: str
    file: file_entity.File
    user_id: uuid.UUID
    status: HistoryStatus = HistoryStatus.CREATED


class HistoryProcessDTO(BaseDTO):
    id: uuid.UUID
    file: bytes


class HistoryUpdateDTO(BaseDTO):
    id: uuid.UUID
    error: str | None
    user_id: uuid.UUID
    status: str
    result: dict | None
