import secrets
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_ignore_empty=True,
        extra='ignore',
        )
    SECRET_KEY = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
    POSTGRES_SERVER: str
    POSTGRES_PORT = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ''
    POSTGRES_DB: str


settings = Settings()
