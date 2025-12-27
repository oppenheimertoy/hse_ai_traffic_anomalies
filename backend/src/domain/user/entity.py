from dataclasses import dataclass

from src.domain.entity import BaseEntity


@dataclass(frozen=True)
class User(BaseEntity): 
    username: str
    password: str