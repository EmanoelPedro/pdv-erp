# PDV Local-First

Bootstrap inicial de um sistema de PDV e controle operacional para uma loja familiar de salgados, pastel, caldo de cana, lanches, hamburguer e pizza.

## Stack

- Backend: Python 3.13+, FastAPI, SQLAlchemy, SQLite, Alembic, Pydantic, Ruff, Pytest, uv
- Frontend: Vue 3, Vite, TypeScript, Pinia, TailwindCSS, base PWA, pnpm

## Estrutura

- `backend/`: API local, configuracao, banco e testes
- `frontend/`: shell da interface, roteamento, estado global e base PWA
- `docs/`: documentacao curta de arquitetura e decisoes

## Comandos

### Backend

- `cd backend && uv run --python "$(command -v python3)" uvicorn app.main:app --reload`
- `cd backend && uv run --python "$(command -v python3)" pytest`
- `cd backend && uv run --python "$(command -v python3)" ruff check .`
- `cd backend && uv run --python "$(command -v python3)" alembic upgrade head`
- `cd backend && uv run --python "$(command -v python3)" alembic current`

### Frontend

- `cd frontend && pnpm install`
- `cd frontend && pnpm dev`
- `cd frontend && pnpm build`
- `cd frontend && pnpm desktop:prepare-backend`
- `cd frontend && pnpm desktop:prepare-python`
- `cd frontend && pnpm desktop:dev`
- `cd frontend && pnpm desktop:build:linux`
- `cd frontend && pnpm desktop:build:windows`
- `cd frontend && pnpm lint`

### Raiz

- `make backend-dev`
- `make frontend-dev`
- `make desktop-dev`
- `make desktop-build`
- `make desktop-build-linux`
- `make desktop-build-windows`
- `make lint`
- `make test`
- `make backend-migrate`
- `make backend-migrate-status`
- `make local-release-build`

## Feature atual

O primeiro fluxo vertical de negocio ja implementado e o de sessao de caixa:

- abrir caixa com valor inicial
- consultar o caixa aberto atual
- fechar caixa com valor contado
- calcular diferenca de fechamento
- exigir PIN do proprietario para o fechamento

O PIN usado por padrao no bootstrap e `1234` e pode ser alterado por `OWNER_ACTION_PIN` em `backend/.env`.

## Escopo atual

Esta etapa implementa a fundacao do projeto e o primeiro recurso real de negocio, focado em controle do caixa. Vendas, despesas e relatorios operacionais completos entram depois sobre essa base.

## Observacao de ambiente

Neste ambiente Linux, o `uv` encontrou primeiro um Python 3.13 sem suporte a `sqlite3`. Os comandos do backend usam explicitamente o `python3` do sistema para garantir suporte a SQLite.

## Entrega local para usuario final

Para entregar em uma maquina Linux sem expor fluxo de desenvolvimento, gere um pacote local com `make local-release-build`.

Esse pacote:

- builda o frontend para producao
- empacota backend e frontend em uma release versionada
- instala em uma pasta fixa com dados fora da versao
- permite atualizar para a versao 2.0 sem sobrescrever `pdv.db` ou `media/`

Veja [docs/local-linux-release.md](docs/local-linux-release.md) para o fluxo de instalacao, inicializacao e atualizacao.

Veja [docs/architecture.md](docs/architecture.md) para a visao geral das camadas e tradeoffs.

Veja [docs/desktop-development.md](docs/desktop-development.md) para o fluxo desktop com Tauri, supervisor do backend local e pre requisitos nativos de Linux e Windows.
