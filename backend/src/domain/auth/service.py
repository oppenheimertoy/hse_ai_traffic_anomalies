import abc
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

import jwt
import src.domain.auth.dto as auth_dto
from cryptography.fernet import Fernet
from src.adapters.database.sqlalchemy import make_sqla_session
from src.adapters.repository.sqlalchemy.token import SqlaTokenRepository
from src.adapters.repository.sqlalchemy.user import SqlaUserRepository
from src.config import CONFIG
from src.domain.auth import entity
from src.domain.auth.errors import TokenExpiredError, TokenNotFoundError
from src.domain.uow import AbstractUnitOfWork

ACCESS_TOKEN_TYPE = "access_token"
REFRESH_TOKEN_TYPE = "refresh_token"


class AbstractAuthMethod:
    pass


class BasicAuthMethod(AbstractAuthMethod):
    Authorization = "Basic "


class JWTAuthMethod(AbstractAuthMethod):
    Authorization = "Bearer "


class AbstractAuthenticationStrategy(abc.ABC):
    auth_method: AbstractAuthMethod

    @abc.abstractmethod
    async def get_credentials(self, token: str) -> entity.Credentials: ...


class EncryptProvider:
    def __init__(self, fernet_key: str):
        self.fernet = Fernet(fernet_key.encode())

    def decrypt(self, encrypted_token: str) -> str:
        return self.fernet.decrypt(encrypted_token).decode()

    def encrypt(self, plain_token: str) -> bytes:
        return self.fernet.encrypt(plain_token.encode())


class JWTAuthenticationStrategy(AbstractAuthenticationStrategy):
    auth_method = JWTAuthMethod.Authorization
    _public_key_pem: str | None = None
    _private_key_pem: str | None = None

    @staticmethod
    def _key_path(filename: str) -> Path:
        base_dir = Path(__file__).resolve().parents[3]
        return base_dir / filename

    @classmethod
    def _get_public_key(cls) -> str:
        if cls._public_key_pem is None:
            cls._public_key_pem = cls._key_path("jwtRS256.key.pub").read_text()
        return cls._public_key_pem

    @classmethod
    def _get_private_key(cls) -> str:
        if cls._private_key_pem is None:
            cls._private_key_pem = cls._key_path("jwtRS256.key").read_text()
        return cls._private_key_pem
    @staticmethod
    def _jwt_algorithm() -> str:
        return CONFIG.JWT_ALGORITHM.strip()

    @staticmethod
    def create_access_token(subject: Dict[str, Any]) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=CONFIG.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        )
        payload = {
            "sub": subject["username"],
            "user_id": subject["user_id"],
            "exp": expire,
            "type": ACCESS_TOKEN_TYPE,
        }
        return jwt.encode(
            payload,
            JWTAuthenticationStrategy._get_private_key(),
            algorithm=JWTAuthenticationStrategy._jwt_algorithm(),
        )

    @staticmethod
    def create_refresh_token(subject: Dict[str, any]) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            days=CONFIG.JWT_REFRESH_TOKEN_EXPIRE_DAYS,
        )
        payload = {
            "sub": subject["username"],
            "user_id": subject["user_id"],
            "exp": expire,
            "type": REFRESH_TOKEN_TYPE,
        }
        data = jwt.encode(
            payload,
            JWTAuthenticationStrategy._get_private_key(),
            algorithm=JWTAuthenticationStrategy._jwt_algorithm(),
        )
        return data

    @classmethod
    def _validate_token(cls: type["JWTAuthenticationStrategy"], token: str) -> dict:
        token_data = jwt.decode(
            token,
            cls._get_public_key(),
            algorithms=[cls._jwt_algorithm()],
        )
        return {
            "user_id": token_data.get("user_id"),
            "username": token_data.get("sub"),
            "expires_at": token_data.get("exp"),
            "type": token_data.get("type"),
        }

    async def get_credentials(self, token: str) -> entity.Credentials:
        token_data = self._validate_token(token)
        if token_data["expires_at"] < datetime.now(timezone.utc).timestamp():
            raise TokenExpiredError()
        return entity.Credentials(token_data["user_id"], token_data["username"])


class BasicAuthenticationStrategy(AbstractAuthenticationStrategy):
    auth_method = BasicAuthMethod.Authorization

    async def get_credentials(self, token: str) -> entity.Credentials:
        session = make_sqla_session()
        token_repo = SqlaTokenRepository(session=session)
        token: entity.Token = await token_repo.get_by_token_value(token)
        
        if not token:
            raise TokenNotFoundError()
        if token.expires_at < datetime.now():
            raise TokenExpiredError()
        user_repo = SqlaUserRepository(session=session)
        user = await user_repo.get(token.user_id)
        token.user = user
        return entity.Credentials(token.user_id, token.user.username)


class AuthService:
    def __init__(self):
        self._strategy: AbstractAuthenticationStrategy = JWTAuthenticationStrategy

    async def authenticate(self, method: str, content: str) -> entity.Credentials:
        self._strategy = self._get_authentication_strategy(method)
        creds: entity.Credetials = await self._strategy.get_credentials(token=content)
        return creds

    def create_access_token(self, username: str, user_id: str) -> str:
        return JWTAuthenticationStrategy.create_access_token(
            subject={"username": username, "user_id": user_id},
        )

    def create_refresh_token(self, username: str, user_id: str) -> str:
        return JWTAuthenticationStrategy.create_refresh_token(
            subject={"username": username, "user_id": user_id},
        )

    def _get_authentication_strategy(self, method: str) -> AbstractAuthenticationStrategy:
        method_normalized = method.strip().lower()
        if method_normalized == BasicAuthMethod.Authorization.strip().lower():
            return BasicAuthenticationStrategy()
        else:
            return JWTAuthenticationStrategy()

    async def create_basic_token(self, uow: AbstractUnitOfWork, dto: auth_dto.TokenCreateDTO) -> entity.Token: 
        return await uow.tokens.create(dto)
    
    async def get_user_tokens(self, uow: AbstractUnitOfWork, user_id: uuid.UUID) -> List[entity.Token]: 
        return await uow.tokens.get_by_user(user_id=user_id)