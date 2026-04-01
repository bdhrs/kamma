#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

exec uv run --project "$SCRIPT_DIR" python "$SCRIPT_DIR/scripts/sync.py"
