#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARTIFACTS_DIR="$ROOT_DIR/.release"
VERSION="${1:-$(grep '^version = ' "$ROOT_DIR/backend/pyproject.toml" | cut -d '"' -f 2)}"
PACKAGE_DIR="$ARTIFACTS_DIR/pdv-local-linux-$VERSION"
RELEASE_DIR="$PACKAGE_DIR/release"

mkdir -p "$ARTIFACTS_DIR"
rm -rf "$PACKAGE_DIR"
mkdir -p "$RELEASE_DIR/backend"
mkdir -p "$RELEASE_DIR/frontend-dist"

echo "[1/4] Buildando frontend"
(cd "$ROOT_DIR/frontend" && pnpm install --frozen-lockfile && pnpm build)

echo "[2/4] Copiando backend"
cp -R "$ROOT_DIR/backend/app" "$RELEASE_DIR/backend/"
cp -R "$ROOT_DIR/backend/migrations" "$RELEASE_DIR/backend/"
cp "$ROOT_DIR/backend/alembic.ini" "$RELEASE_DIR/backend/"
cp "$ROOT_DIR/backend/pyproject.toml" "$RELEASE_DIR/backend/"
cp "$ROOT_DIR/backend/README.md" "$RELEASE_DIR/backend/"
cp "$ROOT_DIR/backend/.env.example" "$RELEASE_DIR/backend/"
cp "$ROOT_DIR/backend/uv.lock" "$RELEASE_DIR/backend/"

echo "[3/4] Copiando frontend buildado"
cp -R "$ROOT_DIR/frontend/dist/." "$RELEASE_DIR/frontend-dist/"
printf '%s\n' "$VERSION" > "$RELEASE_DIR/VERSION"

echo "[4/4] Gerando pacote"
cp "$ROOT_DIR/scripts/local_release_lib.sh" "$PACKAGE_DIR/local_release_lib.sh"
cp "$ROOT_DIR/scripts/install_local_release.sh" "$PACKAGE_DIR/install.sh"
cp "$ROOT_DIR/scripts/update_local_release.sh" "$PACKAGE_DIR/update.sh"
cp "$ROOT_DIR/docs/local-linux-release.md" "$PACKAGE_DIR/README.md"
chmod +x "$PACKAGE_DIR/install.sh" "$PACKAGE_DIR/update.sh" "$PACKAGE_DIR/local_release_lib.sh"
tar -czf "$ARTIFACTS_DIR/pdv-local-linux-$VERSION.tar.gz" -C "$ARTIFACTS_DIR" "pdv-local-linux-$VERSION"

echo "Pacote gerado em $ARTIFACTS_DIR/pdv-local-linux-$VERSION.tar.gz"