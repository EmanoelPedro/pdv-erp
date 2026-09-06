from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.exception_handlers import register_exception_handlers
from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging(get_settings().log_level)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    Path(settings.resolved_media_dir).mkdir(parents=True, exist_ok=True)
    frontend_dist_dir = Path(settings.frontend_dist_dir).resolve()
    frontend_index_file = frontend_dist_dir / "index.html"
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    app.mount("/media", StaticFiles(directory=settings.resolved_media_dir), name="media")
    app.include_router(api_router)

    if frontend_index_file.is_file():

        @app.get("/{frontend_path:path}", include_in_schema=False)
        async def serve_frontend(frontend_path: str) -> FileResponse:
            requested_path = frontend_dist_dir / frontend_path
            if frontend_path and requested_path.is_file():
                return FileResponse(requested_path)

            return FileResponse(frontend_index_file)

    return app


app = create_app()
