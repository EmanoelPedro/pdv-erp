#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/local_release_lib.sh"

INSTALL_DIR="$(default_install_dir "${1:-}")"
VERSION="$(bundle_version "$SCRIPT_DIR")"

require_python_313
prepare_shared_dirs "$INSTALL_DIR"
stage_release "$SCRIPT_DIR" "$INSTALL_DIR" "$VERSION"
prepare_venv "$INSTALL_DIR"
install_backend_package "$INSTALL_DIR" "$VERSION"
switch_current_release "$INSTALL_DIR" "$VERSION"
write_runtime_scripts "$INSTALL_DIR"

echo "Release $VERSION instalada em $INSTALL_DIR"
echo "Use $INSTALL_DIR/start-pdv.sh para iniciar o sistema."