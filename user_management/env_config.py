from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", env_file_encoding="utf-8", extra="ignore")
    DATABASE_URL: str
    ALLOWED_HOSTS: str = "*"


env = Settings()
