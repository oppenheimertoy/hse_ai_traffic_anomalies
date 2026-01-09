from datetime import datetime
import enum
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


class File(Base): 
    created_by: UUID
    file_url: str
    file: bytes

class History(Base):
    user_id: UUID
    status: str
    file_url: str | None
    result: dict | None
    error: str | None
