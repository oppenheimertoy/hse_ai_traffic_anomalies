from uuid import UUID
from sqlalchemy import select
from src.adapters.repository.sqlalchemy.user import SqlaUserRepository
from src.adapters.database.models import UserToken, User
from src.adapters.repository.sqlalchemy.base import BaseCrudRepository
from src.domain.auth.repository import AbstractTokenRepository
from src.domain.auth import entity as auth_entity
import src.domain.user.entity as user_entity

class SqlaTokenRepository(BaseCrudRepository[UserToken], AbstractTokenRepository):
    model = UserToken

    @classmethod
    def map(cls, obj: UserToken, user: user_entity.User) -> auth_entity.Token:
        val = auth_entity.Token(
            id=obj.id,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            deleted=obj.deleted,
            deleted_at=obj.deleted_at,
            user=user,
            user_id=user.id,
            expires_at=obj.expired_at,
        )
        return val

    async def get_by_user(self, user_id: UUID) -> list[auth_entity.Token] | None:
        query = select(self.model).where(self.model.user_id == user_id)
        result = await self._session.execute(query)
        tokens = result.scalars().all()
        user = await SqlaUserRepository(self._session).get(user_id)
        if len(tokens) > 0:
            return [self.map(token, user) for token in tokens]
        return None

    async def get_by_token_value(self, value):
        query = select(self.model).where(self.model.token == value)
        result = await self._session.execute(query)
        result = result.scalar()
        if result: 
            user = await SqlaUserRepository(self._session).get(result.user_id)
            return self.map(result, user)