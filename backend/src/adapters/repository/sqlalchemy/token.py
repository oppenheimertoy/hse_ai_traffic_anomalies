import random
import secrets
import string
from typing import List
from uuid import UUID
from sqlalchemy import select
from src.adapters.repository.sqlalchemy.user import SqlaUserRepository
from src.adapters.database.models import UserToken, User
from src.adapters.repository.sqlalchemy.base import BaseCrudRepository
from src.domain.auth.repository import AbstractTokenRepository
from src.domain.auth import entity as auth_entity
from src.domain.auth.dto import TokenCreateDTO
import src.domain.user.entity as user_entity

class SqlaTokenRepository(BaseCrudRepository[UserToken], AbstractTokenRepository):
    model = UserToken

    @classmethod
    def map(cls, obj: UserToken) -> auth_entity.Token:
        val = auth_entity.Token(
            id=obj.id,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            deleted=obj.deleted,
            deleted_at=obj.deleted_at,
            user_id=obj.user_id,
            token=obj.token,
            expires_at=obj.expires_at,
        )
        return val

    async def get_by_user(self, user_id: UUID) -> List[auth_entity.Token] | None:
        query = select(self.model).where(self.model.user_id == user_id)
        result = await self._session.execute(query)
        tokens = result.scalars().all()
        if len(tokens) == 0: 
            return None
        if len(tokens) > 0:
            return [self.map(token) for token in tokens]

    async def get_by_token_value(self, value: string) -> auth_entity.Token | None:
        query = select(self.model).where(self.model.token == value)
        result = await self._session.execute(query)
        result = result.scalar()
        if result: 
            
            return self.map(result)
    async def create(self, dto: TokenCreateDTO) -> auth_entity.Token | None:
        chars = string.ascii_letters + string.digits
        dto.token = ''.join(secrets.choice(chars) for _ in range(32))
        dto.expires_at = dto.expires_at.replace(tzinfo=None)
        return await super().create(dto)