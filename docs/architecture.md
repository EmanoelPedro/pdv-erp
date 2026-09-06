# Arquitetura

## Visão geral

O PDV Local é uma aplicação local-first para uma única loja. O SQLite é a fonte de verdade e o fluxo operacional principal não depende de um serviço externo.

```text
Vue/PWA ──HTTP──┐
                ├── FastAPI ── serviços ── repositórios ── SQLite
Tauri ──HTTP────┘                                  └────── mídia local
```

No navegador, frontend e backend são iniciados separadamente durante o desenvolvimento. No desktop, o shell Tauri inicia o backend, escolhe uma porta local livre e entrega a URL à interface.

## Backend

O backend em `backend/app/` é um monólito modular:

- `api/`: rotas HTTP, dependências e tratamento de erros
- `core/`: configuração e logging
- `database/`: engine, sessões, modelos ORM e migrações
- `domain/`: entidades e regras que não dependem de HTTP
- `repositories/`: consultas e persistência
- `services/`: casos de uso e transações
- `schemas/`: contratos de entrada e saída com Pydantic

Os módulos cobrem autenticação, usuários, catálogo, vendas, sessões de caixa, despesas, dashboard, relatórios e fila de sincronização.

### Caixa e vendas

- apenas uma sessão de caixa pode permanecer aberta
- vendas aceitam um ou mais meios de pagamento
- o valor esperado é `abertura + dinheiro recebido - despesas pagas em dinheiro`
- somente o proprietário autenticado pode fechar o caixa
- a diferença é calculada entre o valor contado e o valor esperado

### Autenticação

- o primeiro usuário cadastrado recebe o papel de proprietário
- PINs são armazenados com PBKDF2, salt aleatório e comparação em tempo constante
- tokens de sessão são aleatórios e somente seus hashes são persistidos
- sessões expiram e podem ser revogadas pelo CLI de suporte

## Frontend

O frontend em `frontend/src/` é organizado por páginas, componentes, serviços HTTP, stores Pinia e tipos compartilhados dentro da aplicação.

A tela de caixa concentra o fluxo rápido de venda. Recursos administrativos, como catálogo, usuários, despesas e relatórios, são restritos ao proprietário.

A PWA mantém os recursos estáticos em cache e possui uma fila de background sync para vendas. Ela ainda precisa alcançar a API local para consolidar os dados; não existe sincronização com uma nuvem nesta versão.

## Runtime desktop

O Tauri preserva a fronteira HTTP e atua como supervisor do backend:

- inclui o código do backend e um runtime Python dedicado no bundle
- inicia `python -m app.local_server` em `127.0.0.1` com porta dinâmica
- define o diretório persistente de banco, mídia e logs
- aguarda `/health/ready` antes de montar a interface
- encerra o processo do backend ao fechar a aplicação

## Sincronização futura

A tabela `sync_queue` registra mutações locais em JSON com os estados `PENDING`, `SYNCED` e `FAILED`. A estrutura estabelece a fronteira para uma integração futura, mas ainda não há worker, API remota ou política de resolução de conflitos.

## Trade-offs

- SQLite reduz a complexidade operacional e atende ao escopo de uma loja por instalação
- o monólito modular mantém as regras explícitas sem introduzir infraestrutura distribuída
- a fronteira HTTP permite reutilizar o frontend no navegador e no desktop
- o runtime Python aumenta o tamanho do instalador, mas evita exigir Python na máquina do usuário desktop
- funcionalidades fiscais, estoque avançado e sincronização em nuvem permanecem fora do escopo atual
