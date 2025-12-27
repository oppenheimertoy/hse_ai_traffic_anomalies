import abc
import src.domain.user.entity as entity

class AbstractUserRepository(abc.ABC): 
    @abc.abstractmethod
    async def get_by_username(self, username: str) -> entity.User:
        ...