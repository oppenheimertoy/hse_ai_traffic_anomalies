from backend.src.adapters.repository.sqlalchemy.base import BaseCrudRepository


class SqlaHistoryRepository(BaseCrudRepository[History], AbstractHistoryRepository):
    ...