from typing import List

import pytz
from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    WEBAPP_HOST: str
    LOCALSTACK_HOST: str
    LOCALSTACK_PORT: int
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION_NAME: str
    AWS_S3_BUCKET_NAME: str

    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    ADMIN_PHONE_NUMBER: str
    ADMIN_EMAIL: EmailStr

    RABBITMQ_USERNAME: str
    RABBITMQ_PASSWORD: str

    @property
    def db_url(self) -> str:
        return f"{self.DB_ENGINE}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB_NUM}"

    @property
    def localstack_url(self) -> str:
        return f"{config.LOCALSTACK_HOST}:{config.LOCALSTACK_PORT}"

    def get_timezone(self):
        return pytz.timezone(self.TIMEZONE)


config = Settings()
