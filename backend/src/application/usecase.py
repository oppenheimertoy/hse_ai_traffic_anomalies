import hashlib

import src.domain.user.dto as user_dto
from src.application.uow_manager import AbstractUoWManager
from src.domain.auth.service import AuthService
from src.domain.user import entity
from src.domain.user.error import (
    UserExistsError,
    UserNotFoundError,
    UserValidationError,
)
from src.domain.user.service import UserService


class Usecase:
    def __init__(
        self,
        uow_manager: AbstractUoWManager,
        user_service: UserService,
        auth_service: AuthService,
    ):
        self._uow_manager = uow_manager
        self.user_service = user_service
        self.auth_service = auth_service

    async def register_user(self, data: user_dto.UserCreateDTO) -> entity.User | None:
        async with self._uow_manager as uow:
            try:
                password = hashlib.sha256(data.password.encode()).hexdigest()
                data.password = password
                created_user = await self.user_service.create_user(uow, data)
                await self._uow_manager.commit()
                return created_user
            except:
                await self._uow_manager.rollback()
                await self._uow_manager.clean()
                raise

    async def login_user(self, data: user_dto.UserLoginDTO) -> entity.User | None:
        async with self._uow_manager as uow:
            try:
                password = hashlib.sha256(data.password.encode()).hexdigest()
                user = await self.user_service.get_user_by_username(uow, data.username)
                print("user: ", user)
                print(password, user.password)
                if not user:
                    raise UserNotFoundError
                if user.password != password:
                    raise UserValidationError
                return user
            except:
                await self._uow_manager.rollback()
                await self._uow_manager.clean()
                raise

    async def get_user_by_username(self, username: str) -> entity.User:
        async with self._uow_manager as uow:
            try:
                user = await self.user_service.get_user_by_username(uow, username)
                if not user:
                    raise UserNotFoundError
                return user
            except:
                await self._uow_manager.rollback()
                await self._uow_manager.clean()
                raise
            
