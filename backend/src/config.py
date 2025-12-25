from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    DEVELOP: bool = True

    POSTGRES_HOST: str 
    POSTGRES_PORT: int 
    POSTGRES_USER: str 
    POSTGRES_PASSWORD: str 
    POSTGRES_DB: str

    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str 
    MINIO_SECRET_KEY: str 

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(env_nested_delimiter="__",env_file='.env')

CONFIG = Config()
