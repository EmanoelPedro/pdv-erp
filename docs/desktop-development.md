# Desenvolvimento Desktop

## Objetivo

O modo desktop adiciona um shell Tauri ao frontend atual sem substituir o fluxo web/PWA.

Hoje o runtime desktop funciona assim:

- Tauri abre a janela nativa
- um supervisor em Rust sobe o backend Python local automaticamente
- o supervisor escolhe uma porta localhost livre em tempo de execucao
- o backend usa o diretorio de dados da aplicacao para banco, midia e logs
- o frontend espera o endpoint `/health/ready` antes de liberar a aplicacao

O frontend continua chamando HTTP normalmente. Nao existe IPC de negocio.

## Comandos

Fluxo web atual:

- `make frontend-dev`
- `make backend-dev`
- `make test`

Fluxo desktop:

- `make desktop-dev`
- `make desktop-build`
- `make desktop-build-linux`
- `make desktop-build-windows`

Comandos diretos no frontend:

- `pnpm desktop:prepare-backend` copia `backend/app`, `backend/migrations` e `backend/alembic.ini` para `frontend/src-tauri/resources/backend`
- `pnpm desktop:prepare-python` cria um runtime Python dedicado em `frontend/src-tauri/resources/python`, instala as dependencias do backend e reutiliza o ambiente quando `backend/pyproject.toml` nao muda
- `pnpm desktop:preflight` verifica no Linux se `pkg-config` enxerga GTK/WebKit antes de chamar o Tauri
- `pnpm desktop:dev` roda o preflight, prepara backend e runtime Python e so depois inicia o shell Tauri
- `pnpm desktop:build:linux` gera bundles Linux (`appimage` e `deb`)
- `pnpm desktop:build:windows` gera bundles Windows (`msi` e `nsis`)

## Supervisor local

O supervisor desktop fica no shell Tauri e resolve o backend nesta ordem:

1. `PDV_BACKEND_WORKDIR`, se informado
2. `backend/` do repo, durante `tauri dev`
3. `resources/backend` dentro do bundle desktop

O interpretador Python e resolvido nesta ordem:

1. `PDV_BACKEND_PYTHON`, se informado
2. `src-tauri/resources/python/...` no workspace, se existir
3. `resources/python/...` dentro do bundle, se existir
4. `python3` no Linux ou `python` no Windows

Variaveis injetadas automaticamente pelo supervisor:

- `ENVIRONMENT=desktop`
- `DATA_DIR=<diretorio de dados da aplicacao>`
- `API_HOST=127.0.0.1`
- `API_PORT=<porta livre escolhida em runtime>`

Logs minimos do backend vao para `logs/backend.log` dentro do diretorio de dados da aplicacao.

## Suporte local

O banco do desktop instalado fica em `~/.local/share/com.pdv.local/pdv.db` por padrao.

Para suporte inicial do PDV sem editar SQLite manualmente, o backend agora expõe um CLI local:

- `pdv-local-support list-users`
- `pdv-local-support set-username --current-username <atual> --new-username <novo>`
- `pdv-local-support set-pin --username <usuario> --pin <novo-pin>`
- `pdv-local-support clear-sessions`
- `pdv-local-support clear-sessions --username <usuario>`
- `pdv-local-support activate-user --username <usuario>`
- `pdv-local-support deactivate-user --username <usuario>`

No app empacotado Linux, o comando pode ser executado com o Python embutido se o launcher ainda nao estiver no `PATH`:

```bash
/usr/lib/PDV\ Local/resources/python/bin/python3 -m app.support_cli list-users
```

Isso facilita diagnosticar problemas de login, confirmar qual `username` realmente foi salvo, resetar PIN e revogar sessoes antigas.

No modo desenvolvimento, o Vite precisa subir exatamente em `127.0.0.1:5173`. O fluxo desktop agora usa `strictPort` para falhar cedo se outra instancia do Vite ja estiver ocupando essa porta, em vez de mudar silenciosamente para `5174+` e quebrar o `devUrl` do Tauri.

## Pre requisitos comuns

- Node.js LTS
- `pnpm`
- Rust via `rustup`
- toolchain Rust `1.88.0` ou superior para o shell desktop atual
- Python `3.13+` para o backend local em desenvolvimento ou quando nao houver runtime Python embutido

Mesmo com o runtime Python embutido para dev/build desktop, o host de build ainda precisa ter um Python funcional para gerar esse runtime localmente.

## Linux

Baseado nos pre requisitos atuais do Tauri v2 e no que o projeto efetivamente precisou neste ambiente, um host Debian/Ubuntu deve ter pelo menos:

```bash
sudo apt update
sudo apt install \
  libglib2.0-dev \
  libgtk-3-dev \
  libgdk-pixbuf-2.0-dev \
  libpango1.0-dev \
  libwebkit2gtk-4.1-dev \
  build-essential \
  curl \
  wget \
  file \
  libxdo-dev \
  libssl-dev \
  libayatana-appindicator3-dev \
  librsvg2-dev \
  pkg-config \
  libdbus-1-dev
```

Notas:

- `pkg-config` e `libdbus-1-dev` sao obrigatorios neste repo para o `cargo check` e `tauri build` passarem no Linux.
- Se o `make desktop-dev` falhar com mensagens sobre `glib-2.0`, `gobject-2.0`, `gio-2.0`, `gdk-pixbuf-2.0` ou `pango`, os pacotes `libglib2.0-dev`, `libgtk-3-dev`, `libgdk-pixbuf-2.0-dev` e `libpango1.0-dev` ainda nao estao visiveis para o `pkg-config`.
- O shell desktop usa WebKitGTK no Linux, entao as dependencias nativas precisam estar presentes mesmo que o frontend Vue build corretamente.
- Os scripts `desktop:build` e `desktop:build:linux` exportam `APPIMAGE_EXTRACT_AND_RUN=1` automaticamente no Linux e, se o passo interno de AppImage do Tauri ainda falhar, repetem o `linuxdeploy` manualmente sobre o `AppDir` gerado para concluir o bundle.
- Gere build Linux em Linux nativo ou CI Linux. Isso reduz atrito com empacotamento `deb` e `appimage`.

## Windows

Pre requisitos nativos principais para desenvolvimento/build local em Windows:

- Microsoft C++ Build Tools com a opcao `Desktop development with C++`
- Microsoft Edge WebView2 Runtime
- Rust `1.88.0+`
- Node.js LTS + `pnpm`
- Python `3.13+` para o backend local enquanto o runtime Python nao estiver embutido no bundle

Para build de bundle desktop neste projeto, o runtime Python agora e preparado no momento do build e copiado para `resources/python`.

Observacoes de build:

- Windows 10 1803+ e Windows 11 normalmente ja trazem WebView2 instalado.
- Se o build gerar MSI, a feature opcional `VBSCRIPT` pode ser necessaria caso o sistema tenha desabilitado esse componente.
- O caminho mais confiavel para `make desktop-build-windows` e executar o build em Windows nativo ou em CI Windows.
- Cross compile Linux/macOS para Windows com NSIS e possivel, mas e mais fragil; para este projeto nao e o caminho principal nesta etapa.

## Estado atual do empacotamento

O shell desktop ja:

- sobe e encerra o backend automaticamente
- injeta porta dinamica
- prepara `resources/backend` no bundle
- prepara `resources/python` com runtime e dependencias do backend
- grava logs minimos

O proximo endurecimento de distribuicao passa a ser reduzir o tamanho do runtime Python embutido e padronizar o empacotamento final por sistema operacional.