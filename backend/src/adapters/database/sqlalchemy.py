from typing import Final

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from src.config import CONFIG

DB_DRIVER: Final[str] = "postgresql+asyncpg"
DB_CONN_POOL_SIZE: Final[int] = 50
DB_QUERY_ECHO: Final[bool] = False
DB_POOL_ECHO: Final[bool] = False


def get_db_dsn() -> URL:
    return URL.create(
        drivername=DB_DRIVER,
        username=CONFIG.POSTGRES_USER,
        password=CONFIG.POSTGRES_PASSWORD,
        host=CONFIG.POSTGRES_HOST,
        port=CONFIG.POSTGRES_PORT,
        database=CONFIG.POSTGRES_DB,
    )

asyncio_engine = create_async_engine(
    get_db_dsn(),
    pool_size=DB_CONN_POOL_SIZE,
    max_overflow=10,
    pool_pre_ping=True,
    echo=DB_QUERY_ECHO,
    echo_pool=DB_POOL_ECHO,
    pool_timeout=30,
)

make_sqla_session = async_sessionmaker(
    asyncio_engine,
    expire_on_commit=False,
)
