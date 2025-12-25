from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.adapters.database.sqlalchemy import make_sqla_session
from src.adapters.uow import UOWManager
from src.api.http.v1.middleware import add_exception_handlers
from src.application.usecase import Usecase
from src.domain.user.service import UserService


def make_uow_manager() -> UOWManager:
    return UOWManager(session_factory=make_sqla_session)

def make_user_service() -> UserService:
    return UserService()

def make_usecase() -> Usecase: 
    return Usecase(
        uow_manager=make_uow_manager(),
        user_service=make_user_service(),
    )

def make_app(api_router: APIRouter) -> FastAPI: 
    app = FastAPI()
    app.include_router(api_router)
    add_exception_handlers(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
