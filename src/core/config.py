from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./steam_dev.db"
    JWT_SECRET: str = "dev_secret_change_in_prod"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    APP_ENV: str = "development"
    APP_NAME: str = "Steam Manager"
    APP_VERSION: str = "1.0.0"
    ADMIN_EMAIL: str = "admin@steam.com"
    ADMIN_PASSWORD: str = "Admin1234!"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
