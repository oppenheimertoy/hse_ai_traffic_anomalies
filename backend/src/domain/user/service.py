import uuid

import src.domain.user.dto as dto
from src.domain.uow import AbstractUnitOfWork
from src.domain.user import entity
from src.domain.user.error import UserExistsError


class UserService:
    async def get_user_by_username(
        self, uow: AbstractUnitOfWork, username: str,
    ) -> entity.User | None:
        return await uow.users.get_by_username(username)

    async def get_user_by_id(self, uow: AbstractUnitOfWork, user_id: uuid.UUID)-> entity.User:
        return await uow.users.get(user_id)

    async def create_user(
        self, uow: AbstractUnitOfWork, data: dto.UserCreateDTO,
    ) -> entity.User:
        is_already_exists = await uow.users.get_by_username(data.username)
        if is_already_exists is not None:
            raise UserExistsError
        return await uow.users.create(data)
