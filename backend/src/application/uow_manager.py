import abc
from types import TracebackType

from src.domain.uow import AbstractUnitOfWork


class AbstractUoWManager(abc.ABC):
    _uow: AbstractUnitOfWork | None

    @abc.abstractmethod
    async def commit(self) -> None: ...

    @abc.abstractmethod
    async def rollback(self) -> None: ...

    @abc.abstractmethod
    async def _create_uow(self) -> AbstractUnitOfWork: ...

    @abc.abstractmethod
    async def _close_uow(self) -> None: ...

    async def create(self) -> AbstractUnitOfWork:
        self._uow = await self._create_uow()
        return self._uow

    async def clean(self) -> None:
        if self._uow:
            await self._close_uow()
            self._uow = None

    async def __aenter__(self) -> AbstractUnitOfWork:
        return await self.create()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.clean()
