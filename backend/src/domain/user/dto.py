from uuid import UUID

from src.domain.dto import BaseDTO


class UserCreateDTO(BaseDTO):
    username: str
    password: str


class UserUpdateDTO(BaseDTO):
    id: UUID
    username: str
    password: str

class UserLoginDTO(BaseDTO):
    username: str
    password: str