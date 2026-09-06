from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.local_runtime import run_pending_migrations
from app.main import app, create_app

client = TestClient(app)


def test_healthcheck() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "pdv-backend"}


def test_versioned_healthcheck() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "pdv-backend",
        "version": "v1",
    }


def test_readiness_healthcheck_reports_ready_when_database_is_migrated(
    monkeypatch,
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "pdv.db"
    media_dir = tmp_path / "media"

    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path}")
    monkeypatch.setenv("MEDIA_DIR", str(media_dir))
    get_settings.cache_clear()
    run_pending_migrations(get_settings())

    readiness_app = create_app()

    with TestClient(readiness_app) as readiness_client:
        root_response = readiness_client.get("/health/ready")
        versioned_response = readiness_client.get("/api/v1/health/ready")

    get_settings.cache_clear()

    assert root_response.status_code == 200
    assert root_response.json() == {
        "status": "ok",
        "service": "pdv-backend",
        "database": "ok",
        "migrations": "ready",
    }
    assert versioned_response.status_code == 200
    assert versioned_response.json() == {
        "status": "ok",
        "service": "pdv-backend",
        "version": "v1",
        "database": "ok",
        "migrations": "ready",
    }


def test_readiness_healthcheck_reports_pending_migrations(
    monkeypatch,
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "pending.db"
    media_dir = tmp_path / "media"

    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path}")
    monkeypatch.setenv("MEDIA_DIR", str(media_dir))
    get_settings.cache_clear()

    readiness_app = create_app()

    with TestClient(readiness_app) as readiness_client:
        response = readiness_client.get("/health/ready")

    get_settings.cache_clear()

    assert response.status_code == 503
    assert response.json() == {"detail": "Database migrations are pending for the local runtime."}


def test_versioned_healthcheck_allows_frontend_origin() -> None:
    response = client.get(
        "/api/v1/health",
        headers={"Origin": "http://localhost:5173"},
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_frontend_dist_falls_back_to_index(monkeypatch, tmp_path: Path) -> None:
    frontend_dist = tmp_path / "frontend-dist"
    frontend_dist.mkdir()
    (frontend_dist / "index.html").write_text(
        "<html><body>pdv local</body></html>", encoding="utf-8"
    )
    (frontend_dist / "manifest.webmanifest").write_text('{"name":"PDV"}', encoding="utf-8")

    monkeypatch.setenv("FRONTEND_DIST_DIR", str(frontend_dist))
    get_settings.cache_clear()

    frontend_app = create_app()

    with TestClient(frontend_app) as frontend_client:
        root_response = frontend_client.get("/")
        route_response = frontend_client.get("/caixa")
        manifest_response = frontend_client.get("/manifest.webmanifest")
        api_response = frontend_client.get("/api/v1/health")

    get_settings.cache_clear()

    assert root_response.status_code == 200
    assert "pdv local" in root_response.text
    assert route_response.status_code == 200
    assert "pdv local" in route_response.text
    assert manifest_response.status_code == 200
    assert manifest_response.text == '{"name":"PDV"}'
    assert api_response.status_code == 200
