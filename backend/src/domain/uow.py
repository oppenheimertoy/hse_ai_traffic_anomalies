import abc

from src.domain.auth.repository import AbstractTokenRepository
from src.domain.file.repository import AbstractFileRepository
from src.domain.history.repository import AbstractHistoryRepository
from src.domain.user.repository import AbstractUserRepository


class AbstractUnitOfWork(abc.ABC):
    # todo: fill with repos
    users: AbstractUserRepository
    tokens: AbstractTokenRepository
    history: AbstractHistoryRepository
    files: AbstractFileRepository