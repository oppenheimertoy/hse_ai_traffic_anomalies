import src.domain.errors as errors
import src.domain.file.entity as file_entity
import src.domain.user.entity as user_entity
from sqlalchemy import exc, select
from src.adapters.database.models import File, User
from src.adapters.repository.sqlalchemy.base import BaseCrudRepository
from src.domain.file.repository import AbstractFileRepository

from backend.src.domain.file.dto import FileCreateDTO


class SqlaFileRepository(BaseCrudRepository[File], AbstractFileRepository):
    model = File

    @classmethod
    def map(cls, obj: File) -> file_entity.File:
        print(obj.__dict__)
        return file_entity.File(
            id=obj.id,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            deleted=obj.deleted,
            deleted_at=obj.deleted_at,
            file_url=obj.file_url,
            created_by=obj.created_by,
        )

    async def create(
        self,
        dto: FileCreateDTO,
        user: user_entity.User,
    ) -> file_entity.File:
        if not dto.file_url:
            raise errors.IntegrityError("file_url is required")  # noqa: TRY003
        try:
            user_model = (
                await self._session.execute(select(User).where(User.id == user.id))
            ).scalar_one()

            obj = File(
                created_by=user.id,
                file_url=dto.file_url,
                user=user_model,
            )
            self._session.add(obj)
            await self._session.flush()
            await self._session.refresh(obj)

        except exc.IntegrityError as e:
            raise errors.IntegrityError(str(e.orig))
        return self.map(obj)
