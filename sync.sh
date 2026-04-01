#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if ! command -v uv &>/dev/null; then
    echo "Error: uv is not installed. Install it from https://docs.astral.sh/uv/" >&2
    exit 1
fi

exec uv run --project "$SCRIPT_DIR" python "$SCRIPT_DIR/scripts/sync.py"
