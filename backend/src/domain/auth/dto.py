import datetime
import uuid

from src.domain.dto import BaseDTO


class TokenCreateDTO(BaseDTO):
    expires_at: datetime.datetime
    user_id: uuid.UUID
    token: str | None