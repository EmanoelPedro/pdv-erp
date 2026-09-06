# Entrega local via navegador no Linux

Além do aplicativo Tauri, o projeto oferece um pacote Linux simples que executa backend e frontend no navegador da máquina do usuário.

## Estrutura

Cada versão é instalada separadamente e os dados persistentes ficam em `shared/`:

```text
pdv-local/
  .venv/
  current -> releases/0.1.0/
  releases/
    0.1.0/
      VERSION
      backend/
      frontend-dist/
  shared/
    pdv.db
    media/
    logs/
  run-server.sh
  start-pdv.sh
  stop-pdv.sh
```

Uma atualização troca a release ativa sem sobrescrever o banco ou as imagens.

## Gerar o pacote

Na raiz do repositório:

```bash
make local-release-build
```

Os arquivos são gerados em:

- `.release/pdv-local-linux-<versao>/`
- `.release/pdv-local-linux-<versao>.tar.gz`

## Instalar

Pré-requisitos da máquina de destino:

- Linux
- Python 3.13 ou superior
- `python3 -m venv` funcional ou `uv` instalado
- acesso à internet na primeira instalação para baixar dependências Python

```bash
tar -xzf pdv-local-linux-0.1.0.tar.gz
cd pdv-local-linux-0.1.0
./install.sh "$HOME/pdv-local"
```

Inicie e encerre a aplicação com:

```bash
$HOME/pdv-local/start-pdv.sh
$HOME/pdv-local/stop-pdv.sh
```

O servidor fica disponível em `http://127.0.0.1:8000` e o navegador é aberto automaticamente quando possível.

## Atualizar

Execute o script da nova versão no mesmo diretório de instalação:

```bash
tar -xzf pdv-local-linux-0.2.0.tar.gz
cd pdv-local-linux-0.2.0
./update.sh "$HOME/pdv-local"
```

O processo instala a nova release, atualiza o ambiente Python, preserva `shared/pdv.db` e `shared/media/` e reinicia o servidor caso ele já estivesse em execução.

## Quando usar este formato

Este pacote é útil para uma instalação Linux controlada e acessada pelo navegador. Para uma distribuição autocontida e com experiência nativa, prefira os bundles Tauri descritos em [desktop-development.md](desktop-development.md).
