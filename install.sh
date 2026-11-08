#!/usr/bin/env bash
# ollama-speak one-line installer for Linux and macOS
set -e

echo "=================================================="
echo " 🗣️ Installing ollama-speak (Multilingual Voice CLI)"
echo "=================================================="

# Check for Python 3.9+
if command -v python3 >/dev/null 2>&1; then
    PY_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PY_BIN="python"
else
    echo "[!] Error: Python 3.9+ is required but not found."
    exit 1
fi

# Detect pipx or pip
if command -v pipx >/dev/null 2>&1; then
    echo "→ Installing via pipx..."
    pipx install --upgrade git+https://github.com/AjarnSpencer/ollama-speak.git || pipx install --upgrade ollama-speak
else
    echo "→ Installing via user pip..."
    $PY_BIN -m pip install --user --upgrade git+https://github.com/AjarnSpencer/ollama-speak.git || $PY_BIN -m pip install --user --upgrade ollama-speak
fi

echo "=================================================="
echo " ✓ Installation complete!"
echo " Run: 'ollama-speak \"Hello world\"'"
echo " Or pipe: 'echo \"Reading from pipe\" | ollama-speak'"
echo "=================================================="
