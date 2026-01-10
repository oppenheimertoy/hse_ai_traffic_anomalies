import enum
from dataclasses import dataclass
from uuid import UUID

from src.domain.entity import BaseEntity


class HistoryStatus(enum.Enum):
    CREATED = "CREATED"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    ERROR = "ERROR"


@dataclass
class History(BaseEntity):
    user_id: UUID
    status: HistoryStatus
    file_url: str | None
    result: dict | None
    error: str | None
    file_id: UUID
