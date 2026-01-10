import hashlib
import uuid
from typing import List

import src.domain.auth.dto as auth_dto
import src.domain.history.entity as history_entity
import src.domain.user.dto as user_dto
from src.adapters.storage.minio import MinioStorage
from src.application.uow_manager import AbstractUoWManager
from src.domain.auth import entity as auth_entity
from src.domain.auth.service import AuthService
from src.domain.file.dto import FileCreateDTO
from src.domain.file.error import (
    FileDownloadError,
    FileUploadError,
)
from src.domain.file.service import FileService
from src.domain.history.dto import HistoryCreateDTO
from src.domain.history.service import HistoryService
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
        storage: MinioStorage,
        user_service: UserService,
        auth_service: AuthService,
        file_service: FileService,
        history_service: HistoryService,
    ):
        self._uow_manager = uow_manager
        self.user_service = user_service
        self.auth_service = auth_service
        self.file_service = file_service
        self.history_service = history_service
        self.storage = storage

    async def register_user(
        self, data: user_dto.UserCreateDTO
    ) -> user_entity.User | None:
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

    async def create_user_token(
        self, dto: auth_dto.TokenCreateDTO
    ) -> auth_entity.Token:
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
                if tokens is None:
                    return []
            except:
                await self._uow_manager.rollback()
                await self._uow_manager.clean()
                raise
            return tokens

    async def forward_pcap(
        self,
        pcap: FileCreateDTO,
    ) -> history_entity.History:
        created_record = await self._create_pcap_file(pcap)
        return created_record

    async def _create_pcap_file(self, pcap: FileCreateDTO):
        async with self._uow_manager as uow:
            try:
                file = await self.file_service.store_file_meta(uow, self.storage, pcap)
                history_dto = HistoryCreateDTO(
                    file_url=file.file_url,
                    file=file,
                    user_id=pcap.user_id,
                )
                history = await self.history_service.create_history(
                    uow,
                    history_dto,
                )
                await self._uow_manager.commit()
                await self.history_service.push_history_to_queue(history)
            except:
                await self._uow_manager.rollback()
                await self._uow_manager.clean()
                raise
            return history

    async def get_history_items(self, ids: List[uuid.UUID]) -> List[history_entity.History]:
        async with self._uow_manager as uow:
            return await self.history_service.list_histories(uow, ids)
