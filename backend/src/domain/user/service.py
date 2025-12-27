import src.domain.user.entity as entity
from src.domain.uow import AbstractUnitOfWork
from src.domain.user.error import UserExistsError


class UserService: 
    async def get_user_by_username(self, uow: AbstractUnitOfWork, username: str) -> entity.User | None: 
        return await uow.users.get_by_username(username)
    async def create_user(self, uow: AbstractUnitOfWork, data: entity.User) -> entity.User: 
        is_already_exists = await uow.users.get_by_username(data.username)
        if is_already_exists != None: 
            raise UserExistsError
        return await uow.users.create(data)
