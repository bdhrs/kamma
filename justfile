default:
    @just --list

sync *args:
    uv run scripts/sync.py {{args}}

test *args:
    uv run pytest {{args}}
