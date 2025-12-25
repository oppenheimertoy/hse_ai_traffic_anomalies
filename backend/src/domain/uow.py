import abc

from src.domain.user.repository import AbstractUserRepository


class AbstractUnitOfWork(abc.ABC):
    # todo: fill with repos
    users: AbstractUserRepository