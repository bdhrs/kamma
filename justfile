default:
    @just --list

sync *args:
    uv run scripts/sync.py {{args}}
