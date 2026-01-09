import abc
import uuid
from collections.abc import Collection
from typing import Any, Generic, Self, TypeVar

from sqlalchemy import exc, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.database.models import Base
from src.domain import errors

_TM = TypeVar("_TM", bound=Base)


class BaseCrudRepository(abc.ABC, Generic[_TM]):
    model: type[_TM]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @classmethod
    @abc.abstractmethod
    def map(cls: type[Self], obj: _TM) -> Any: ...  # noqa: ANN401

    async def create(self, dto: Any) -> Any:  # noqa: ANN401
        try:
            cmd = (
                insert(self.model)
                .values(dto.model_dump(exclude_unset=True))
                .returning(self.model)
            )
            result = await self._session.execute(cmd)

            obj = result.unique().scalar_one()
        except exc.IntegrityError as e:
            raise errors.IntegrityError(str(e.orig))
        return self.map(obj)

    async def create_many(self, create_dtos: Collection[Any]) -> list[Any]:
        if not create_dtos:
            return []
        try:
            query = (
                insert(self.model)
                .values([dto.model_dump(exclude_unset=True) for dto in create_dtos])
                .returning(self.model)
            )
            result = await self._session.execute(query)
            objects = result.unique().scalars().all()
        except exc.IntegrityError as e:
            raise errors.IntegrityError(str(e.orig))
        return [self.map(obj) for obj in objects]

    async def get(self, obj_id: Any) -> Any:  # noqa: ANN401
        query = select(self.model).filter_by(id=obj_id)
        result = await self._session.execute(query)
        obj = result.unique().scalar_one_or_none()
        if not obj:
            msg = f"<{self.model.__name__}> with id={obj_id} not found in repository"
            raise errors.NotFoundError(msg)

        return self.map(obj)

    async def update(self, id: uuid.UUID, dto: Any) -> Any:
        query = select(self.model).filter_by(id=id)
        result = await self._session.execute(query)
        obj = result.unique().scalar_one_or_none()
        if not obj:
            msg = f"<{self.model.__name__}> with id={id} not found in repository"
            raise errors.NotFoundError(msg)
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

    async def delete(self, id: str) -> bool:
        query = select(self.model).filter_by(id=id)
        result = await self._session.execute(query)
        obj = result.unique().scalar_one_or_none()
        if not obj:
            msg = f"<{self.model.__name__}> with id={id} not found in repository"
            raise errors.NotFoundError(msg)
        try:
            cmd = (
                update(self.model)
                .where(self.model.id == id)
                .values(deleted_at=func.now(), deleted=True)
                .returning(self.model)
            )
            await self._session.execute(cmd)
        except exc.IntegrityError as e:
            raise errors.IntegrityError(str(e.orig))
        return True
