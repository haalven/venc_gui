#!/usr/bin/env bash
set -euo pipefail

APP_NAME="venc_gui"
ENTRYPOINT="venc_gui.py"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found in PATH" >&2
  exit 1
fi

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt pyinstaller

# Build a native macOS .app bundle in dist/
python3 -m PyInstaller \
  --noconfirm \
  --windowed \
  --name "$APP_NAME" \
  "$ENTRYPOINT"

echo "Build complete: dist/${APP_NAME}.app"
