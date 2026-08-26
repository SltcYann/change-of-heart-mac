#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv-macos"
PYTHON_BIN="${PYTHON_BIN:-/opt/homebrew/bin/python3}"

# Prefer the standalone Command Line Tools. This avoids inheriting a selected
# Xcode beta whose xcrun/lipo architecture may not match the running macOS.
if [[ -d /Library/Developer/CommandLineTools ]]; then
  export DEVELOPER_DIR=/Library/Developer/CommandLineTools
fi

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Python 3 est introuvable. Installez-le avec : brew install python@3.14"
  exit 1
fi

cd "$SCRIPT_DIR"
"$PYTHON_BIN" -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -r requirements-build.txt
"$VENV_DIR/bin/python" -m unittest discover -s tests
"$VENV_DIR/bin/python" -m PyInstaller P5R_Save_Editor.spec --noconfirm --clean --distpath dist

echo
echo "Build terminé : $SCRIPT_DIR/dist/Change of Heart.app"
