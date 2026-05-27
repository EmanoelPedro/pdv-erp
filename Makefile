PYTHON_BIN := $(shell command -v python3)

backend-dev:
	cd backend && uv run --python $(PYTHON_BIN) uvicorn app.main:app --reload

backend-test:
	cd backend && uv run --python $(PYTHON_BIN) pytest

backend-lint:
	cd backend && uv run --python $(PYTHON_BIN) ruff check .

frontend-dev:
	cd frontend && pnpm dev

frontend-build:
	cd frontend && pnpm build

desktop-dev:
	cd frontend && pnpm desktop:dev

desktop-build:
	cd frontend && pnpm desktop:build

desktop-build-linux:
	cd frontend && pnpm desktop:build:linux

desktop-build-windows:
	cd frontend && pnpm desktop:build:windows

frontend-lint:
	cd frontend && pnpm lint

local-release-build:
	./scripts/build_local_release.sh

lint: backend-lint frontend-lint

test: backend-test frontend-build

backend-migrate-status:
	cd backend && uv run --python $(PYTHON_BIN) alembic current

backend-migrate:
	cd backend && uv run --python $(PYTHON_BIN) alembic upgrade head
