default:
    @just --list

sync:
    uv run scripts/sync.py

kammika-rebuild:
    uv tool install --force --reinstall-package kammika ./kammika
