from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.database import get_db, models  # noqa: F401
from app.database.base import Base
from app.main import create_app


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=Session,
    )

    Base.metadata.create_all(bind=engine)
    session = testing_session_local()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def client(
    db_session: Session,
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[TestClient, None, None]:
    monkeypatch.setenv("MEDIA_DIR", str(tmp_path / "media"))
    get_settings.cache_clear()
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    get_settings.cache_clear()


@pytest.fixture
def owner_auth_headers(client: TestClient) -> dict[str, str]:
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Owner User",
            "username": "owner",
            "pin": "1234",
        },
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "owner", "pin": "1234"},
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def employee_auth_headers(
    client: TestClient,
    owner_auth_headers: dict[str, str],
) -> dict[str, str]:
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Employee User",
            "username": "employee",
            "pin": "5678",
            "role": "EMPLOYEE",
        },
        headers=owner_auth_headers,
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "employee", "pin": "5678"},
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
