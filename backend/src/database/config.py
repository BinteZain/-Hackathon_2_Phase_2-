from pydantic_settings import SettingsConfigDict, BaseSettings
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    DATABASE_URL: str
    BETTER_AUTH_SECRET: str = "default_secret_for_dev"


settings = Settings()