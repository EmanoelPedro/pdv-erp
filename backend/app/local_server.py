import uvicorn

from app.core.config import get_settings
from app.local_runtime import run_pending_migrations


def main() -> None:
    settings = get_settings()
    run_pending_migrations(settings)
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
    )


if __name__ == "__main__":
    main()
