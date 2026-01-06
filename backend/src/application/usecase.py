import hashlib
import uuid
from typing import List

import src.domain.auth.dto as auth_dto
import src.domain.user.dto as user_dto
from src.application.uow_manager import AbstractUoWManager
from src.domain.auth import entity as auth_entity
from src.domain.auth.service import AuthService
from src.domain.user import entity as user_entity
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

    async def register_user(self, data: user_dto.UserCreateDTO) -> user_entity.User | None:
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

    async def login_user(self, data: user_dto.UserLoginDTO) -> user_entity.User | None:
        async with self._uow_manager as uow:
            try:
                password = hashlib.sha256(data.password.encode()).hexdigest()
                user = await self.user_service.get_user_by_username(uow, data.username)
                if not user:
                    raise UserNotFoundError
                if user.password != password:
                    raise UserValidationError
                return user
            except:
                await self._uow_manager.rollback()
                await self._uow_manager.clean()
                raise

    async def get_user_by_username(self, username: str) -> user_entity.User:
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
            
    async def create_user_token(self, dto: auth_dto.TokenCreateDTO) -> auth_entity.Token: 
        async with self._uow_manager as uow:
            try: 
                token = await self.auth_service.create_basic_token(uow, dto)
                token_user = await self.user_service.get_user_by_id(uow, token.user_id)
                token.user = token_user
                await self._uow_manager.commit()
                return token
            except: 
                await self._uow_manager.rollback()
                await self._uow_manager.clean()
                raise
            
    async def get_user_tokens(self, user_id: uuid.UUID) -> list[auth_entity.Token]: 
        async with self._uow_manager as uow: 
            try: 
                tokens = await self.auth_service.get_user_tokens(uow, user_id)
                print("tokens:", tokens)
                if tokens is None: return []
                return tokens
            except: 
                await self._uow_manager.rollback()
                await self._uow_manager.clean()
                raise

    async def forward_pcap(self, pcap): 
        async with self._uow_manager as uow: 
            try: 
                