from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.adapters.database.sqlalchemy import make_sqla_session
from src.adapters.uow import UOWManager
from src.api.http.v1.middleware import add_exception_handlers
from src.application.usecase import Usecase


def make_uow_manager() -> UOWManager:
    return UOWManager(session_factory=make_sqla_session)

def make_usecase() -> Usecase: 
    return Usecase()

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
