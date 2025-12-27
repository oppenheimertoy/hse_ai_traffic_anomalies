from sqlalchemy import select
from src.adapters.database.models import User
from src.adapters.repository.sqlalchemy.base import BaseCrudRepository
from src.domain.user import entity
from src.domain.user.repository import AbstractUserRepository


class SqlaUserRepository(BaseCrudRepository[User], AbstractUserRepository):
    model = User

    @classmethod
    def map(cls, obj: User) -> entity.User:
        print(obj)
        return entity.User(
            id=obj.id,
            username=obj.username,
            password=obj.password,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            deleted=obj.deleted,
            deleted_at=obj.deleted_at,
        )

    async def get_by_username(self, username: str) -> entity.User | None:
        query = select(self.model).where(self.model.username == username)
        result = await self._session.execute(query)
        user = result.scalar()
        if user:
            return self.map(user)
        return None
