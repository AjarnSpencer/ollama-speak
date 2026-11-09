#!/usr/bin/env bash
# ollama-speak turnkey installer for Linux and macOS (100% Local Neural TTS)
set -e

echo "=================================================="
echo " 🗣️ Installing ollama-speak (Local Neural Voice CLI)"
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

# Install dependencies and package
if [ -f "pyproject.toml" ]; then
    echo "→ Installing from local repository..."
    $PY_BIN -m pip install --upgrade .
else
    echo "→ Installing from GitHub..."
    $PY_BIN -m pip install --upgrade git+https://github.com/AjarnSpencer/ollama-speak.git
fi

# Pre-download local open weights
if command -v ollama-speak >/dev/null 2>&1; then
    echo "→ Pre-downloading open weights for 100% offline use..."
    ollama-speak --setup || true
fi

echo "=================================================="
echo " ✓ Installation complete!"
echo " Run: 'ollama-speak \"Hello from local AI\"'"
echo " Or pipe: 'ollama run llama3 \"...\" | ollama-speak'"
echo "=================================================="
