from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

import src.domain.user.dto as user_dto
from src.api.http.v1 import schemas
from src.api.http.v1.security import create_access_token, get_current_user
from src.application.usecase import Usecase
from src.deps import make_usecase
from src.domain.user import entity

api_router = APIRouter(prefix='/v1')
auth_router = APIRouter(prefix="/auth")
user_router = APIRouter(prefix='/users')

@api_router.get('/health')
async def health_check() -> dict[str, str]:
    return {'status': 'ok'}

@user_router.post('/register')
async def register_user(
    payload: user_dto.UserCreateDTO,
    usecase: Annotated[Usecase, Depends(make_usecase)],
) -> schemas.User:
    user = await usecase.register_user(payload)
    return schemas.User.model_validate(user)


@auth_router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    usecase: Annotated[Usecase, Depends(make_usecase)],
) -> schemas.Token:
    user = await usecase.login_user(
        user_dto.UserLoginDTO(username=form_data.username, password=form_data.password)
    )
    access_token = create_access_token(subject=user.username)
    return schemas.Token(access_token=access_token, token_type="bearer")


@user_router.get("/me")
async def read_users_me(
    current_user: Annotated[entity.User, Depends(get_current_user)],
) -> schemas.User:
    return schemas.User.model_validate(current_user)

api_router.include_router(auth_router)
api_router.include_router(user_router)
