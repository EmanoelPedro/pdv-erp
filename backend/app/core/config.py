from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PDV API"
    app_version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "INFO"
    data_dir: str | None = None
    database_url: str = "sqlite:///./pdv.db"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    frontend_dist_dir: str = "../frontend/dist"
    cors_allowed_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://tauri.localhost",
        "https://tauri.localhost",
        "tauri://localhost",
    ]
    owner_action_pin: str = "1234"
    auth_session_days: int = 30
    media_dir: str = "media"
    max_product_image_size_bytes: int = 5_000_000

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @property
    def resolved_data_dir(self) -> Path | None:
        if self.data_dir is None:
            return None

        return Path(self.data_dir).expanduser().resolve()

    @property
    def resolved_database_url(self) -> str:
        if self.resolved_data_dir is None or self.database_url != "sqlite:///./pdv.db":
            return self.database_url

        return f"sqlite:///{(self.resolved_data_dir / 'pdv.db').as_posix()}"

    @property
    def resolved_media_dir(self) -> str:
        if self.resolved_data_dir is None or self.media_dir != "media":
            return self.media_dir

        return str((self.resolved_data_dir / "media").resolve())

    @property
    def resolved_logs_dir(self) -> str | None:
        if self.resolved_data_dir is None:
            return None

        return str((self.resolved_data_dir / "logs").resolve())


@lru_cache
def get_settings() -> Settings:
    return Settings()
