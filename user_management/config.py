from typing import List

import pytz
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", env_file_encoding="utf-8", extra="ignore")
    DB_ENGINE: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    WEBAPP_TEST_HOST: str
    ALLOWED_HOSTS: List[str] = ["*"]
    ACCESS_TOKEN_TTL_MINUTES: int = 5
    REFRESH_TOKEN_TTL_DAYS: int = 10
    TIMEZONE: str = "Europe/Minsk"
    SECRET_KEY: str
    TOKEN_HASH_ALGORITHM: str = "HS256"
    REDIS_PORT: int
    REDIS_HOST: str
    REDIS_DB_NUM: int
    SOURCE_EMAIL: EmailStr

    @property
    def db_url(self) -> str:
        return f"{self.DB_ENGINE}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB_NUM}"

    def get_timezone(self):
        return pytz.timezone(self.TIMEZONE)


config = Settings()
