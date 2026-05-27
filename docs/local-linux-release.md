# Entrega Local em Linux

Este projeto agora suporta um pacote local para uso em uma maquina Linux sem expor comandos de desenvolvimento para o usuario final.

## Como funciona

- o backend FastAPI passa a servir o frontend buildado na mesma origem
- cada versao fica em `releases/<versao>`
- os dados persistentes ficam fora da versao, em `shared/`
- a atualizacao troca apenas a release ativa e preserva banco e arquivos de midia

Estrutura instalada:

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

## Gerar o pacote

Na maquina de desenvolvimento:

```bash
cd /home/emanoel-pedro/projects/erp-workspace/pdv
make local-release-build
```

Saida gerada:

- `.release/pdv-local-linux-<versao>/`
- `.release/pdv-local-linux-<versao>.tar.gz`

## Instalar na maquina do usuario

Pre requisitos da maquina alvo:

- Linux
- Python 3.13 ou superior
- `python3 -m venv` funcional ou `uv` instalado na maquina
- acesso a internet na instalacao inicial para baixar dependencias Python

Passos:

```bash
tar -xzf pdv-local-linux-0.1.0.tar.gz
cd pdv-local-linux-0.1.0
./install.sh "$HOME/pdv-local"
```

Depois disso, o usuario inicia com:

```bash
$HOME/pdv-local/start-pdv.sh
```

O script sobe o servidor local em `http://127.0.0.1:8000` e tenta abrir o navegador automaticamente.

Para encerrar:

```bash
$HOME/pdv-local/stop-pdv.sh
```

## Atualizar para a versao 2.0

Na nova release:

```bash
tar -xzf pdv-local-linux-2.0.0.tar.gz
cd pdv-local-linux-2.0.0
./update.sh "$HOME/pdv-local"
```

O update:

- copia a nova release para `releases/2.0.0/`
- reinstala o backend na virtualenv local
- aponta `current` para a nova versao
- preserva `shared/pdv.db` e `shared/media/`
- reinicia o servidor se ele ja estava aberto

## Por que esse modelo e o mais limpo aqui

- o usuario final lida com dois scripts: iniciar e atualizar
- voce nao sobrescreve dados ao trocar a versao
- rollback e simples: basta apontar `current` para a release anterior
- o backend e o frontend rodam juntos no mesmo endereco local

## Limite atual

Esse fluxo resolve bem Linux local com baixo atrito. Se voce quiser distribuicao sem depender de Python na maquina alvo, o proximo passo correto e empacotar o backend como binario nativo ou criar um instalador do sistema operacional.