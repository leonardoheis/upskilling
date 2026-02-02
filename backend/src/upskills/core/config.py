from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "UpSkills API"
    app_version: str = "0.1.0"
    debug: bool = False

    server_host: str = "0.0.0.0"
    server_port: int = 8000

    # Database
    database_path: str = "upskills.db"

    # JWT Authentication
    secret_key: str = "change-me-in-production-use-a-secure-random-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    @property
    def database_url(self) -> str:
        return f"sqlite+aiosqlite:///{self.database_path}"

    @property
    def project_root(self) -> Path:
        return Path(__file__).parent.parent.parent.parent.parent


@lru_cache
def get_settings() -> Settings:
    return Settings()
