from app.core.config import get_settings


def test_default_settings() -> None:
    settings = get_settings()

    assert settings.app_name == "PDV API"
    assert settings.database_url == "sqlite:///./pdv.db"
    assert settings.resolved_database_url == "sqlite:///./pdv.db"
    assert settings.frontend_dist_dir == "../frontend/dist"
    assert settings.api_host == "127.0.0.1"
    assert settings.api_port == 8000
    assert "http://localhost:5173" in settings.cors_allowed_origins
    assert "http://tauri.localhost" in settings.cors_allowed_origins
    assert "https://tauri.localhost" in settings.cors_allowed_origins
    assert "tauri://localhost" in settings.cors_allowed_origins
