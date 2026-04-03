#!/usr/bin/env bash
set -euo pipefail

REPO_ZIP="https://github.com/bdhrs/kamma/archive/refs/heads/main.zip"
INSTALL_DIR="$HOME/kamma"

# Check for uv
if ! command -v uv &>/dev/null; then
    echo "uv is not installed. uv is required to run kamma."
    printf "Install it now? [y/N] "
    read -r answer </dev/tty
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
    else
        echo "Aborted."
        exit 1
    fi
fi

# Download and extract
echo "Downloading kamma..."
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

curl -sSL "$REPO_ZIP" -o "$TMP_DIR/kamma.zip"
unzip -q "$TMP_DIR/kamma.zip" -d "$TMP_DIR"

rm -rf "$INSTALL_DIR"
mv "$TMP_DIR/kamma-main" "$INSTALL_DIR"

# Run sync
echo "Syncing..."
cd "$INSTALL_DIR"
uv run python scripts/sync.py
