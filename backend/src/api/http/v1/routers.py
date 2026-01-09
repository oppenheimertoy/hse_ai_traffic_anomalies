from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.security import OAuth2PasswordRequestForm

import src.domain.auth.dto as auth_dto
import src.domain.auth.entity as auth_entity
import src.domain.user.dto as user_dto
from backend.src.domain.file.dto import FileCreateDTO
from src.api.http.v1 import schemas
from src.application.usecase import Usecase
from src.deps import make_usecase

api_router = APIRouter(prefix="/v1")
auth_router = APIRouter(prefix="/auth")
user_router = APIRouter(prefix="/users")
token_router = APIRouter(prefix="/tokens")


@api_router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@user_router.post("/register")
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
) -> schemas.JWTToken:
    dto = user_dto.UserLoginDTO(
        username=form_data.username,
        password=form_data.password,
    )
    user = await usecase.login_user(
        dto,
    )
    access_token = usecase.auth_service.create_access_token(
        username=user.username,
        user_id=str(user.id),
    )
    refresh_token = usecase.auth_service.create_refresh_token(
        username=user.username,
        user_id=str(user.id),
    )
    return schemas.JWTToken(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@user_router.get("/me")
async def read_users_me(
    request: Request,
    usecase: Annotated[Usecase, Depends(make_usecase)],
) -> schemas.User:
    return await usecase.get_user_by_username(request.state.username)


@api_router.get("/test")
async def test_token() -> bool:
    return True


@api_router.post("/forward")
async def recieve_pcap_file(
    request: Request,
    usecase: Annotated[Usecase, Depends(make_usecase)],
    pcap: UploadFile = File(...),
) -> schemas.History:
    if not pcap.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing file name.",
        )
    ext = Path(pcap.filename).suffix.lower()
    if ext not in {".pcap", ".csv"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .pcap or .csv files are allowed.",
        )
    user_id = request.state.user_id
    dto = FileCreateDTO(file=await pcap.read(), user_id=user_id)
    return await usecase.forward_pcap(dto)


@token_router.post("/")
async def create_basic_token(
    request: Request,
    usecase: Annotated[Usecase, Depends(make_usecase)],
    payload: schemas.TokenCreate,
) -> auth_entity.Token:
    user_id = request.state.user_id
    return await usecase.create_user_token(
        auth_dto.TokenCreateDTO(
            user_id=user_id,
            expires_at=payload.expires_at,
            token=None,
        ),
    )


@token_router.get("/")
async def get_all_tokens(
    request: Request,
    usecase: Annotated[Usecase, Depends(make_usecase)],
) -> list[auth_entity.Token]:
    tokens = await usecase.get_user_tokens(user_id=request.state.user_id)
    return tokens


user_router.include_router(token_router)
api_router.include_router(auth_router)
api_router.include_router(user_router)
