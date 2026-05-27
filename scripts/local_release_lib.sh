#!/usr/bin/env bash

set -euo pipefail

default_install_dir() {
  printf '%s\n' "${1:-$HOME/pdv-local}"
}

require_python_313() {
  if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 nao encontrado. Instale Python 3.13+ antes de continuar." >&2
    exit 1
  fi

  if ! python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 13) else 1)'; then
    echo "Python 3.13+ e obrigatorio para instalar esta release." >&2
    exit 1
  fi
}

bundle_version() {
  local bundle_dir="$1"
  tr -d '[:space:]' < "$bundle_dir/release/VERSION"
}

stage_release() {
  local bundle_dir="$1"
  local install_dir="$2"
  local version="$3"
  local release_dir="$install_dir/releases/$version"

  mkdir -p "$install_dir/releases"
  rm -rf "$release_dir"
  mkdir -p "$release_dir"
  cp -R "$bundle_dir/release/." "$release_dir/"
}

prepare_shared_dirs() {
  local install_dir="$1"

  mkdir -p "$install_dir/shared/media"
  mkdir -p "$install_dir/shared/logs"
}

prepare_venv() {
  local install_dir="$1"
  local python3_bin

  python3_bin="$(command -v python3)"

  if [[ ! -x "$install_dir/.venv/bin/python" ]]; then
    if python3 -m venv "$install_dir/.venv" >/dev/null 2>&1; then
      return
    fi

    rm -rf "$install_dir/.venv"

    if command -v uv >/dev/null 2>&1; then
      uv venv --clear --python "$python3_bin" "$install_dir/.venv"
      return
    fi

    echo "Nao foi possivel criar a virtualenv com python3 -m venv e o comando uv nao esta disponivel." >&2
    echo "Instale o pacote python3-venv ou o utilitario uv antes de continuar." >&2
    exit 1
  fi
}

install_backend_package() {
  local install_dir="$1"
  local version="$2"
  local release_dir="$install_dir/releases/$version"
  local python_bin="$install_dir/.venv/bin/python"

  if "$python_bin" -m pip --version >/dev/null 2>&1; then
    "$python_bin" -m pip install --upgrade pip
    "$python_bin" -m pip install --upgrade --force-reinstall "$release_dir/backend"
    return
  fi

  if command -v uv >/dev/null 2>&1; then
    uv pip install --python "$python_bin" --reinstall "$release_dir/backend"
    return
  fi

  echo "A virtualenv foi criada, mas pip nao esta disponivel e o comando uv nao foi encontrado." >&2
  exit 1
}

switch_current_release() {
  local install_dir="$1"
  local version="$2"

  ln -sfn "$install_dir/releases/$version" "$install_dir/current"
}

write_runtime_scripts() {
  local install_dir="$1"

  cat <<'EOF' > "$install_dir/run-server.sh"
#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURRENT_DIR="$ROOT_DIR/current"
BACKEND_DIR="$CURRENT_DIR/backend"
FRONTEND_DIR="$CURRENT_DIR/frontend-dist"
SHARED_DIR="$ROOT_DIR/shared"

export ENVIRONMENT=production
export DATABASE_URL="sqlite:///$SHARED_DIR/pdv.db"
export MEDIA_DIR="$SHARED_DIR/media"
export FRONTEND_DIST_DIR="$FRONTEND_DIR"

mkdir -p "$SHARED_DIR/media"
mkdir -p "$SHARED_DIR/logs"

cd "$BACKEND_DIR"
"$ROOT_DIR/.venv/bin/python" -m alembic upgrade head
exec "$ROOT_DIR/.venv/bin/python" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
EOF

  cat <<'EOF' > "$install_dir/start-pdv.sh"
#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$ROOT_DIR/shared/pdv-server.pid"
LOG_FILE="$ROOT_DIR/shared/logs/pdv-server.log"
PDV_URL="http://127.0.0.1:8000"

mkdir -p "$ROOT_DIR/shared/logs"

if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" >/dev/null 2>&1; then
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$PDV_URL" >/dev/null 2>&1 || true
  fi
  echo "PDV ja esta em execucao em $PDV_URL"
  exit 0
fi

nohup "$ROOT_DIR/run-server.sh" >> "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"

for _attempt in $(seq 1 40); do
  if curl --silent --fail "$PDV_URL/health" >/dev/null 2>&1; then
    break
  fi
  sleep 0.25
done

if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$PDV_URL" >/dev/null 2>&1 || true
fi

echo "PDV iniciado em $PDV_URL"
EOF

  cat <<'EOF' > "$install_dir/stop-pdv.sh"
#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$ROOT_DIR/shared/pdv-server.pid"

if [[ ! -f "$PID_FILE" ]]; then
  echo "Nenhum processo do PDV foi encontrado."
  exit 0
fi

PID="$(cat "$PID_FILE")"
if kill -0 "$PID" >/dev/null 2>&1; then
  kill "$PID"
  echo "PDV finalizado."
else
  echo "O PID registrado nao esta em execucao."
fi

rm -f "$PID_FILE"
EOF

  chmod +x "$install_dir/run-server.sh" "$install_dir/start-pdv.sh" "$install_dir/stop-pdv.sh"
}
