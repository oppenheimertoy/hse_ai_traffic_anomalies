from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic.config import ConfigDict


class Base(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted: bool
    deleted_at: datetime | None

class User(Base):
    username: str


class JWTToken(BaseModel):
    access_token: str
    refresh_token: str

class TokenCreate(BaseModel): 

    expires_at: datetime
