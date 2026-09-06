# Backend do PDV Local

API local do PDV Local, construída com FastAPI, SQLAlchemy e SQLite.

## Desenvolvimento

```bash
uv sync --locked --all-groups
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

## Verificações

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

As configurações disponíveis estão documentadas em [.env.example](.env.example). Dados locais, mídia e arquivos de ambiente não são versionados.
