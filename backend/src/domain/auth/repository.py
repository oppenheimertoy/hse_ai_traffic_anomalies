import abc
from uuid import UUID

from src.domain.auth import entity


class AbstractTokenRepository(abc.ABC): 
    @abc.abstractmethod
    async def get_by_user(self, user_id: UUID) -> entity.Token:
        ...

    @abc.abstractmethod
    async def get_by_token_value(self, value: str) -> entity.Token | None:
        ...