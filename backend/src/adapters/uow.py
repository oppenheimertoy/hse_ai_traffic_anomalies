from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession
from src.application.uow_manager import AbstractUoWManager
from src.domain.uow import AbstractUnitOfWork


class UnitOfWork(AbstractUnitOfWork):
    def __init__(self, sqla_session: AsyncSession) -> None:
        self._sqla_session: AsyncSession = sqla_session
        # todo: fill with repos
        
    @property
    def sqla_session(self) -> AsyncSession:
        return self._sqla_session

class UOWManager(AbstractUoWManager):
    _uow: UnitOfWork | None = None

    def __init__(self, session_factory: Callable[[], AsyncSession]):
        self._sqla_session_factory = session_factory

    async def _create_uow(self) -> UnitOfWork:
        sqla_session = self._sqla_session_factory()
        self._uow = UnitOfWork(sqla_session)
        return self._uow
    
    async def _close_uow(self) -> None:
        if self._uow: 
            await self._uow.sqla_session.close()
            self._uow = None
    async def commit(self) -> None:
        if self._uow:
            await self._uow.sqla_session.commit()
    
    async def rollback(self) -> None:
        if self._uow:
            await self._uow.sqla_session.rollback()
