import uuid
from typing import List
from uuid import UUID

import src.domain.history.entity as history_entity
from sqlalchemy import func, select, update, exc
from sqlalchemy.orm import selectinload
from src.adapters.database.models import File, History, User
from src.adapters.repository.sqlalchemy.base import BaseCrudRepository
from src.domain import errors
from src.domain.history.dto import HistoryCreateDTO, HistoryUpdateDTO
from src.domain.history.repository import AbstractHistoryRepository


class SqlaHistoryRepository(BaseCrudRepository[History], AbstractHistoryRepository):
    model = History

    @classmethod
    def map(cls, obj: History) -> history_entity.History:
        return history_entity.History(
            id=obj.id,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            deleted=obj.deleted,
            deleted_at=obj.deleted_at,
            user_id=obj.user_id,
            file_id=obj.file_id,
            status=history_entity.HistoryStatus(obj.status),
            error=obj.error,
            result=obj.result,
            file_url=obj.file.file_url,
        )

    async def create(self, dto: HistoryCreateDTO) -> history_entity.History:
        file = (
            await self._session.execute(select(File).where(File.id == dto.file.id))
        ).scalar_one()
        user = (
            await self._session.execute(select(User).where(User.id == dto.user_id))
        ).scalar_one()

        db_obj = self.model(
            result=None,
            user_id=dto.user_id,
            file_id=file.id,
            file=file,
            user=user,
        )
        self._session.add(db_obj)
        await self._session.flush()
        await self._session.refresh(db_obj, ["user"])
        return self.map(db_obj)

    async def update(
        self,
        id: uuid.UUID,
        dto: HistoryUpdateDTO,
    ) -> history_entity.History:
        query = (
            select(self.model)
            .options(selectinload(self.model.file))
            .filter_by(id=id)
        )
        result = await self._session.execute(query)
        obj = result.unique().scalar_one_or_none()
        try:
            values = dto.model_dump(exclude_unset=True, exclude={"id"})
            values["updated_at"] = func.now()
            cmd = (
                update(self.model)
                .where(self.model.id == id)
                .values(values)
                .returning(self.model)
            )
            result = await self._session.execute(cmd)
            obj = result.unique().scalar_one()
        except exc.IntegrityError as e:
            raise errors.IntegrityError(str(e.orig))
        return self.map(obj)

    async def update_status(
        self, id: UUID, history_status: str,
    ) -> history_entity.History:
        query = (
            select(self.model)
            .options(selectinload(self.model.file))
            .where(self.model.id == id)
        )
        result = await self._session.execute(query)
        db_obj = result.scalar_one_or_none()
        if not db_obj:
            msg = f"<{self.model.__name__}> with id={id} not found in repository"
            raise errors.NotFoundError(msg)
        db_obj.status = history_status
        await self._session.flush()
        await self._session.refresh(db_obj, ["file", "updated_at"])
        return self.map(db_obj)

    async def get_all_by_status(self, status: str) -> List[history_entity.History]:
        query = (
            select(self.model)
            .options(selectinload(self.model.file))
            .where(self.model.status == status)
        )
        result = await self._session.execute(query)
        return [self.map(r) for r in result.scalars().all()]
