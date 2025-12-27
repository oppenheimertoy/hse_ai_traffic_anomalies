from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.entity import BaseEntity
from src.domain.user.entity import User

@dataclass(frozen=True)
class Credentials:
    user_id: UUID
    username: str

@dataclass(frozen=True)
class Token(BaseEntity):
    user_id: UUID
    user: User
    expires_at: datetime
