#!/bin/bash
# copy.sh — convert source .md files and copy to all AI CLIs
# Run after editing any commands/*.md file
#
# Usage: ./copy.sh
# just copy
#
# Copys to: Claude Code, Gemini CLI, OpenCode, Kilo CLI, Codex CLI

set -e

KAMMA_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC="$KAMMA_DIR/commands"

echo "Copying kamma from $KAMMA_DIR..."

# --- Claude Code ---
echo "  -> Claude Code"
CLAUDE_DIR="$HOME/.claude/plugins/local/kamma"
mkdir -p "$CLAUDE_DIR/commands/kamma" "$CLAUDE_DIR/.claude-plugin"
cp "$KAMMA_DIR/registration/claude-plugin.json" "$CLAUDE_DIR/.claude-plugin/plugin.json"
# Copy SKILL.md for Claude Code
mkdir -p "$CLAUDE_DIR/skills/kamma"
cp "$KAMMA_DIR/skills/kamma/SKILL.md" "$CLAUDE_DIR/skills/kamma/SKILL.md"
for f in "$SRC"/*.md; do
    base=$(basename "$f" .md)
    # Extract description from frontmatter
    desc=$(sed -n 's/^description: *//p' "$f")
    # Extract body (everything after second ---)
    body=$(sed '1,/^---$/d; 1,/^---$/d' "$f")
    # Write TOML
    printf 'description = "%s"\nprompt = """\n%s\n"""\n' "$desc" "$body" \
        > "$CLAUDE_DIR/commands/kamma/$base.toml"
done

# --- Gemini CLI ---
echo "  -> Gemini CLI"
GEMINI_DIR="$HOME/.gemini/extensions/kamma"
mkdir -p "$GEMINI_DIR/commands/kamma"
cp "$KAMMA_DIR/registration/gemini-extension.json" "$GEMINI_DIR/gemini-extension.json"
cp "$KAMMA_DIR/registration/GEMINI.md" "$GEMINI_DIR/GEMINI.md"
# Gemini uses same TOML format as Claude
cp "$CLAUDE_DIR/commands/kamma/"*.toml "$GEMINI_DIR/commands/kamma/"

# --- OpenCode ---
echo "  -> OpenCode"
OPENCODE_DIR="$HOME/.opencode/command"
mkdir -p "$OPENCODE_DIR"
for f in "$SRC"/*.md; do
    base=$(basename "$f" .md)
    cp "$f" "$OPENCODE_DIR/kamma-$base.md"
done

# --- Codex CLI ---
echo "  -> Codex CLI"
CODEX_DIR="$HOME/.codex/prompts"
mkdir -p "$CODEX_DIR"
for f in "$SRC"/*.md; do
    base=$(basename "$f" .md)
    # Strip YAML frontmatter for Codex
    sed '1,/^---$/d; 1,/^---$/d' "$f" > "$CODEX_DIR/kamma-$base.md"
done

# --- Kilo CLI (skills format: SKILL.md in named dirs) ---
echo "  -> Kilo CLI"
for f in "$SRC"/*.md; do
    base=$(basename "$f" .md)
    KILO_SKILL="$HOME/.kilocode/skills/kamma-$base"
    mkdir -p "$KILO_SKILL"
    # Convert command frontmatter to skill frontmatter
    desc=$(sed -n 's/^description: *//p' "$f")
    body=$(sed '1,/^---$/d; 1,/^---$/d' "$f")
    cat > "$KILO_SKILL/SKILL.md" <<SKILLEOF
---
name: kamma-$base
description: $desc
---

$body
SKILLEOF
done
# Also copy the main skill to Kilo
mkdir -p "$HOME/.kilocode/skills/kamma"
cp "$KAMMA_DIR/skills/kamma/SKILL.md" "$HOME/.kilocode/skills/kamma/SKILL.md"

echo ""
echo "Copied kamma to: Claude Code, Gemini CLI, OpenCode, Kilo CLI, Codex CLI"
