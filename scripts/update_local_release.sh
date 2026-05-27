#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/local_release_lib.sh"

INSTALL_DIR="$(default_install_dir "${1:-}")"
VERSION="$(bundle_version "$SCRIPT_DIR")"
WAS_RUNNING=0

require_python_313

if [[ -x "$INSTALL_DIR/start-pdv.sh" ]] && [[ -f "$INSTALL_DIR/shared/pdv-server.pid" ]]; then
  if kill -0 "$(cat "$INSTALL_DIR/shared/pdv-server.pid")" >/dev/null 2>&1; then
    WAS_RUNNING=1
    "$INSTALL_DIR/stop-pdv.sh"
  fi
fi

prepare_shared_dirs "$INSTALL_DIR"
stage_release "$SCRIPT_DIR" "$INSTALL_DIR" "$VERSION"
prepare_venv "$INSTALL_DIR"
install_backend_package "$INSTALL_DIR" "$VERSION"
switch_current_release "$INSTALL_DIR" "$VERSION"
write_runtime_scripts "$INSTALL_DIR"

if [[ "$WAS_RUNNING" -eq 1 ]]; then
  "$INSTALL_DIR/start-pdv.sh"
fi

echo "Release $VERSION aplicada em $INSTALL_DIR"