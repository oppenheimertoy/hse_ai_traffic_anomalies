from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.src.adapters.storage.minio import MinioStorage
from backend.src.config import CONFIG
from src.adapters.database.sqlalchemy import make_sqla_session
from src.adapters.uow import UOWManager
from src.api.http.v1.middleware import JwtAuthMiddleware, add_exception_handlers
from src.application.usecase import Usecase
from src.domain.auth.service import AuthService
from src.domain.user.service import UserService

def make_storage() -> MinioStorage: 
    return MinioStorage(
    endpoint=CONFIG.MINIO_ENDPOINT,
    access_key=CONFIG.MINIO_ACCESS_KEY,
    secret_key=CONFIG.MINIO_SECRET_KEY,
    bucket=CONFIG.MINIO_BUCKET,
    secure=CONFIG.MINIO_SECURE,
)

def make_uow_manager() -> UOWManager:
    return UOWManager(session_factory=make_sqla_session)


def make_user_service() -> UserService:
    return UserService()


def make_auth_service() -> AuthService:
    return AuthService()


def make_usecase() -> Usecase:
    return Usecase(
        uow_manager=make_uow_manager(),
        user_service=make_user_service(),
        auth_service=make_auth_service(),
    )


def make_app(api_router: APIRouter) -> FastAPI:
    app = FastAPI()
    app.include_router(api_router)
    add_exception_handlers(app)
    app.add_middleware(
        JwtAuthMiddleware,
        authentication_service=make_auth_service(),
        excluded_paths=(
            "/api/v1/health",
            "/api/v1/auth/token",
            "/api/v1/auth/refresh",
            "/api/v1/users/register",
            "/docs",
            "/openapi.json",
            "/redoc",
        ),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Access-Token", "X-Refresh-Token"],
    )
    return app
