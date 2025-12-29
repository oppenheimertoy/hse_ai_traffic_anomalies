from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.entity import BaseEntity
from src.domain.user.entity import User


@dataclass(frozen=True)
class Credentials:
    user_id: UUID
    username: str

@dataclass
class Token(BaseEntity):
    user_id: UUID
    token: str
    expires_at: datetime
    user: User | None = None
