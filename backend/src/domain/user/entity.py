from dataclasses import dataclass

from src.domain.entity import BaseEntity


@dataclass
class User(BaseEntity): 
    username: str
    password: str