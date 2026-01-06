import abc

from backend.src.domain.file.repository import AbstractHistoryRepository
from src.domain.auth.repository import AbstractTokenRepository
from src.domain.user.repository import AbstractUserRepository


class AbstractUnitOfWork(abc.ABC):
    # todo: fill with repos
    users: AbstractUserRepository
    tokens: AbstractTokenRepository
    history: AbstractHistoryRepository