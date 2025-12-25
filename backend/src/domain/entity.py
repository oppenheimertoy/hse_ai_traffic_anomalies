from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class BaseEntity:
    id: UUID
    created_at: datetime
    updated_at: datetime

    deleted: bool
    deleted_at: datetime | None