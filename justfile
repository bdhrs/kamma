default:
    @just --list

sync:
    uv run python scripts/sync.py

kammika-rebuild:
    uv tool install --force --reinstall-package kammika ./kammika
