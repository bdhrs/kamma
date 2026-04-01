#!/bin/bash
# copy.sh — convert source .md files and copy to installed AI CLIs only
# Run after editing any commands/*.md file

set -e

KAMMA_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC="$KAMMA_DIR/commands"
TEMPLATES_SRC="$KAMMA_DIR/templates"

copy_claude() {
    local target="$HOME/.claude/plugins/local/kamma"
    mkdir -p "$target/commands/kamma" "$target/.claude-plugin" "$target/skills/kamma" "$target/templates"
    cp "$KAMMA_DIR/registration/claude-plugin.json" "$target/.claude-plugin/plugin.json"
    cp "$KAMMA_DIR/skills/kamma/SKILL.md" "$target/skills/kamma/SKILL.md"
    for f in "$SRC"/*.md; do
        local base desc body
        base=$(basename "$f" .md)
        desc=$(sed -n 's/^description: *//p' "$f")
        body=$(sed '1,/^---$/d; 1,/^---$/d' "$f")
        printf 'description = "%s"\nprompt = """\n%s\n"""\n' "$desc" "$body" > "$target/commands/kamma/$base.toml"
    done
    cp -R "$TEMPLATES_SRC/." "$target/templates/"
}

copy_gemini() {
    local target="$HOME/.gemini/extensions/kamma"
    mkdir -p "$target/commands/kamma" "$target/templates"
    cp "$KAMMA_DIR/registration/gemini-extension.json" "$target/gemini-extension.json"
    cp "$KAMMA_DIR/registration/GEMINI.md" "$target/GEMINI.md"
    for f in "$SRC"/*.md; do
        local base desc body
        base=$(basename "$f" .md)
        desc=$(sed -n 's/^description: *//p' "$f")
        body=$(sed '1,/^---$/d; 1,/^---$/d' "$f")
        printf 'description = "%s"\nprompt = """\n%s\n"""\n' "$desc" "$body" > "$target/commands/kamma/$base.toml"
    done
    cp -R "$TEMPLATES_SRC/." "$target/templates/"
}

copy_opencode() {
    local command_target="$HOME/.opencode/command"
    local templates_target="$HOME/.opencode/templates/kamma"
    mkdir -p "$command_target" "$templates_target"
    rm -f "$command_target"/kamma-status.md
    for f in "$SRC"/*.md; do
        local base
        base=$(basename "$f" .md)
        cp "$f" "$command_target/kamma-$base.md"
    done
    cp -R "$TEMPLATES_SRC/." "$templates_target/"
}

copy_codex() {
    local prompt_target="$HOME/.codex/prompts"
    local templates_target="$HOME/.codex/templates/kamma"
    mkdir -p "$prompt_target" "$templates_target"
    rm -rf "$HOME/plugins/kamma"
    python3 - <<'PY'
from pathlib import Path
import json

marketplace = Path.home() / '.agents' / 'plugins' / 'marketplace.json'
if marketplace.exists():
    data = json.loads(marketplace.read_text())
    plugins = [p for p in data.get('plugins', []) if p.get('name') != 'kamma']
    if plugins != data.get('plugins', []):
        data['plugins'] = plugins
        marketplace.write_text(json.dumps(data, indent=2) + '\n')
PY
    for f in "$SRC"/*.md; do
        local base
        base=$(basename "$f" .md)
        sed '1,/^---$/d; 1,/^---$/d' "$f" > "$prompt_target/kamma-$base.md"
    done
    cp -R "$TEMPLATES_SRC/." "$templates_target/"
}

copy_kilo() {
    local skills_root="$HOME/.kilocode/skills"
    local templates_target="$HOME/.kilocode/templates/kamma"
    mkdir -p "$skills_root/kamma" "$templates_target"
    for f in "$SRC"/*.md; do
        local base desc body skill_dir
        base=$(basename "$f" .md)
        desc=$(sed -n 's/^description: *//p' "$f")
        body=$(sed '1,/^---$/d; 1,/^---$/d' "$f")
        skill_dir="$skills_root/kamma-$base"
        mkdir -p "$skill_dir"
        cat > "$skill_dir/SKILL.md" <<SKILLEOF
---
name: kamma-$base
description: $desc
---

$body
SKILLEOF
    done
    cp "$KAMMA_DIR/skills/kamma/SKILL.md" "$skills_root/kamma/SKILL.md"
    cp -R "$TEMPLATES_SRC/." "$templates_target/"
}

echo "Copying kamma from $KAMMA_DIR..."

if [ -d "$HOME/.claude" ]; then
    echo "Claude Code: copied"
    copy_claude
else
    echo "Claude Code: skipped"
fi

if [ -d "$HOME/.gemini" ]; then
    echo "Gemini CLI: copied"
    copy_gemini
else
    echo "Gemini CLI: skipped"
fi

if [ -d "$HOME/.opencode" ]; then
    echo "OpenCode: copied"
    copy_opencode
else
    echo "OpenCode: skipped"
fi

if [ -d "$HOME/.codex" ]; then
    echo "Codex CLI: copied"
    copy_codex
else
    echo "Codex CLI: skipped"
fi

if [ -d "$HOME/.kilocode" ]; then
    echo "Kilo CLI: copied"
    copy_kilo
else
    echo "Kilo CLI: skipped"
fi
