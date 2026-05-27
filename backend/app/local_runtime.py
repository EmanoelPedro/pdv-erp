from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from app.core.config import Settings, get_settings


def _backend_root_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def _build_alembic_config(settings: Settings) -> Config:
    backend_root = _backend_root_dir()
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("path_separator", "os")
    config.set_main_option("script_location", str(backend_root / "migrations"))
    config.set_main_option("sqlalchemy.url", settings.resolved_database_url)
    return config


def ensure_runtime_directories(settings: Settings | None = None) -> None:
    runtime_settings = settings or get_settings()
    Path(runtime_settings.resolved_media_dir).mkdir(
        parents=True, exist_ok=True)

    if runtime_settings.resolved_logs_dir is not None:
        Path(runtime_settings.resolved_logs_dir).mkdir(
            parents=True, exist_ok=True)

    database_path = make_url(runtime_settings.resolved_database_url).database
    if database_path and database_path != ":memory:":
        Path(database_path).expanduser().resolve(
        ).parent.mkdir(parents=True, exist_ok=True)


def run_pending_migrations(settings: Settings | None = None) -> None:
    runtime_settings = settings or get_settings()
    ensure_runtime_directories(runtime_settings)
    command.upgrade(_build_alembic_config(runtime_settings), "head")


def get_runtime_readiness(settings: Settings | None = None) -> dict[str, str]:
    runtime_settings = settings or get_settings()
    ensure_runtime_directories(runtime_settings)

    engine = create_engine(
        runtime_settings.resolved_database_url,
        connect_args={"check_same_thread": False}
        if runtime_settings.resolved_database_url.startswith("sqlite")
        else {},
    )

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

            context = MigrationContext.configure(connection)
            current_revision = context.get_current_revision()

        alembic_config = _build_alembic_config(runtime_settings)
        head_revision = ScriptDirectory.from_config(
            alembic_config).get_current_head()

        if current_revision != head_revision:
            raise RuntimeError(
                "Database migrations are pending for the local runtime.")

        return {
            "database": "ok",
            "migrations": "ready",
        }
    finally:
        engine.dispose()
