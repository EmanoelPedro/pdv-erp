# Copilot Instructions

## Project purpose

PDV Local is a local-first point-of-sale system for small businesses. Its primary workflows are authentication, product catalog management, sales, cash-register sessions, expenses, dashboards, and operational reports.

Optimize changes for reliability, fast cashier interactions, simple maintenance, and offline operation. Prefer a small, explicit solution that fits the existing architecture over a new abstraction or dependency.

## Repository map

- `backend/app/api/`: FastAPI routes, dependencies, and exception handlers
- `backend/app/domain/`: business entities, value rules, and domain exceptions
- `backend/app/services/`: use cases, authorization checks, and transaction boundaries
- `backend/app/repositories/`: SQLAlchemy queries and persistence mapping
- `backend/app/schemas/`: Pydantic request and response contracts
- `backend/app/database/`: SQLAlchemy models, engine, and session configuration
- `backend/migrations/`: Alembic migrations
- `backend/tests/`: API and service tests
- `frontend/src/pages/`: route-level Vue components
- `frontend/src/components/`: reusable interface components
- `frontend/src/services/`: HTTP clients grouped by business capability
- `frontend/src/stores/`: Pinia authentication and UI state
- `frontend/src/runtime/`: browser and Tauri runtime bootstrap
- `frontend/src-tauri/`: Tauri shell and local backend supervisor
- `docs/`: architecture and distribution documentation

Do not edit or commit generated content from `frontend/dist/`, `frontend/dev-dist/`, `frontend/src-tauri/resources/`, `frontend/src-tauri/target/`, virtual environments, local databases, logs, or uploaded media.

## Business invariants

- Only one cash-register session may be open at a time.
- A sale requires an open cash-register session.
- A sale may use cash, Pix, debit card, credit card, or a valid combination of methods.
- Expected cash is `opening amount + cash received - cash expenses`.
- Only an authenticated owner may close the cash register or access administrative workflows.
- The first registered user becomes the owner; later registrations require an owner.
- Money must use `Decimal` in Python and the existing normalization helpers. Never use binary floating-point values for business calculations.
- Existing SQLite data must remain valid after an upgrade. Schema changes require an Alembic migration.

## Backend conventions

- Keep HTTP routes thin. Parse the request, resolve dependencies, call a service, and map the result to a response schema.
- Put business decisions in domain objects or services, not in routers or repositories.
- Keep SQLAlchemy access inside repositories. Services own commit and rollback behavior.
- Raise the existing domain exceptions and let the registered exception handlers translate them to HTTP responses.
- Use `app.domain.shared.utc_now()` for timestamps and preserve the project's UTC conventions.
- Use explicit dependency injection through `app.api.dependencies`.
- Follow the neighboring module before introducing a new pattern.
- Add or update service tests for business rules and API tests for HTTP contracts.

## Frontend conventions

- Use Vue 3 Composition API with `<script setup lang="ts">`.
- Keep network access in `src/services/` and shared API shapes in `src/types/`.
- Use Pinia only for state shared across routes; keep page-specific state in the page or a focused composable.
- Reuse PrimeVue components and the existing Tailwind/CSS design language.
- Keep route pages lazy-loaded unless they are part of the application shell.
- Preserve keyboard-first cashier workflows and visible focus behavior.
- User-facing copy is Brazilian Portuguese and must use correct accents. Code identifiers remain in English.
- Do not expose buttons, routes, or shortcuts for unfinished workflows. Document future work under limitations instead.
- Follow the existing error-reading and toast patterns instead of displaying raw server errors.

## Local-first and desktop boundaries

- SQLite is the source of truth for each installation.
- The Tauri shell starts the bundled Python backend on a dynamic loopback port and waits for `/health/ready`.
- Keep the API bound to `127.0.0.1` by default. Do not broaden network exposure without an explicit security design.
- The PWA caches static resources and can queue sales requests, but cloud synchronization is not implemented.
- `sync_queue` is preparation for future synchronization; do not describe it as a working cloud feature.
- Persistent database, media, and logs must stay outside versioned application directories.

## Scope

Current scope includes cash-register operation, sales, payment methods, catalog, users, expenses, dashboards, reports, PWA support, and desktop packaging.

Out of scope unless a change explicitly introduces and tests them:

- fiscal document emission
- advanced inventory management
- loyalty, CRM, or promotions
- cloud synchronization and conflict resolution
- multi-store or multi-tenant operation

## Working guidelines

- Read the relevant service, repository, schema, and tests before changing a backend workflow.
- Keep changes focused and preserve established naming and module boundaries.
- Never add real credentials, PINs, tokens, customer data, databases, or machine-specific paths.
- Update `.env.example`, documentation, and migrations when configuration or persistence changes.
- Update lockfiles with `uv` or `pnpm`; do not edit them manually.
- Avoid speculative abstractions, silent fallbacks, and placeholder implementations.

## Validation

Run the checks relevant to the change. Before considering repository-wide work complete, run from the repository root:

```bash
make lint
make test
pnpm --dir frontend format
cargo fmt --manifest-path frontend/src-tauri/Cargo.toml --check
cargo check --manifest-path frontend/src-tauri/Cargo.toml
```

Backend-only commands:

```bash
cd backend
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Frontend-only commands:

```bash
cd frontend
pnpm lint
pnpm format
pnpm build
```

## Definition of done

A change is complete when the implementation follows the existing architecture, affected behavior is tested, lint and formatting checks pass, generated artifacts remain untracked, and documentation matches the behavior users can actually run.
