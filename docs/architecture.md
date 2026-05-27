# Arquitetura

## Objetivo

Entregar uma base local-first, simples de operar e simples de manter para um sistema de PDV de loja unica.

## Backend

O backend fica em `backend/app/` e segue um modular monolith pragmatica:

- `api/`: adaptadores HTTP e versionamento em `/api/v1`
- `core/`: configuracao e logging
- `database/`: engine, session e base ORM
- `domain/`: entidades e regras puras, incluindo a sessao de caixa
- `repositories/`: acesso a dados persistidos
- `services/`: casos de uso e invariantes de negocio
- `schemas/`: contratos Pydantic de request e response

Hoje a API sobe com healthchecks, migration inicial e o primeiro fluxo real de negocio: sessao de caixa.

### Fluxo de caixa

- apenas uma sessao pode ficar aberta por vez
- o fechamento calcula `difference_amount = closing_amount - expected_amount`
- nesta primeira etapa `expected_amount = opening_amount`
- o fechamento exige PIN do proprietario para proteger alteracoes sensiveis

## Frontend

O frontend fica em `frontend/src/` e organiza a interface em:

- `layouts/`: casca principal da aplicacao
- `pages/`: telas por rota
- `router/`: navegacao
- `services/`: cliente HTTP e integracoes
- `stores/`: estado global com Pinia

Tambem inclui base PWA para instalacao e operacao offline-first sem depender de internet para o core.

## Runtime desktop

O modo desktop usa Tauri como shell nativo e preserva a fronteira HTTP entre frontend e backend:

- o Vue continua consumindo API HTTP normalmente
- o shell Tauri sobe um supervisor local que inicia `python -m app.local_server`
- o supervisor escolhe uma porta localhost livre, injeta `DATA_DIR`, `API_HOST` e `API_PORT`, e grava logs minimos no diretorio de dados da aplicacao
- o frontend espera `/health/ready` antes de montar as rotas, evitando race condition no boot
- o encerramento do app desktop mata o backend local de forma explicita

Isso preserva o modo web/PWA atual e adiciona um runtime desktop paralelo sem acoplar as telas ao shell nativo.

## Fundacao offline-first

Foi adicionada a base da `sync_queue` no backend para preparar sincronizacao futura por eventos:

- tabela `sync_queue` em SQLite via Alembic
- modelo ORM, dominio, repositorio e servico dedicados
- payload armazenado como JSON serializado
- status inicial `PENDING`, com suporte a `SYNCED` e `FAILED`

Ainda nao existe worker de envio, sincronizacao cloud, resolucao de conflito ou replay automatico. O objetivo aqui e apenas criar a fronteira persistente para mutacoes futuras.

## Tradeoffs

- `backend/` e `frontend/` na raiz para reduzir complexidade operacional
- SQLite local como fonte da verdade
- PWA base agora, sincronizacao cloud depois
- Tauri desktop com supervisor local agora, empacotamento completo do runtime Python depois
- fechamento protegido por PIN do proprietario como recorte minimo de permissao, em vez de um sistema completo de autenticacao agora
- nada de CQRS, microservicos ou abstrações especulativas nesta fase
