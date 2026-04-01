#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
COMMANDS_DIR = ROOT / "commands"
TEMPLATES_DIR = ROOT / "templates"
REGISTRATION_DIR = ROOT / "registration"
SKILLS_DIR = ROOT / "skills"
HOME = Path.home()


@dataclass(frozen=True)
class Command:
    base: str
    description: str
    body: str
    source: Path


def read_commands() -> list[Command]:
    commands: list[Command] = []
    for path in sorted(COMMANDS_DIR.glob("*.md")):
        text = path.read_text()
        description, body = split_frontmatter(text, path)
        commands.append(
            Command(
                base=path.stem,
                description=description,
                body=body.rstrip() + "\n",
                source=path,
            )
        )
    return commands


def split_frontmatter(text: str, path: Path) -> tuple[str, str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError(f"{path} is missing YAML frontmatter")

    end_index = None
    for index in range(1, len(lines)):
        if lines[index] == "---":
            end_index = index
            break
    if end_index is None:
        raise ValueError(f"{path} has unclosed YAML frontmatter")

    frontmatter = lines[1:end_index]
    description = ""
    for line in frontmatter:
        if line.startswith("description:"):
            description = line.partition(":")[2].strip()
            break
    if not description:
        raise ValueError(f"{path} is missing a description field")

    body = "\n".join(lines[end_index + 1 :]).lstrip("\n")
    return description, body


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def copy_tree_contents(src: Path, dest: Path) -> None:
    ensure_dir(dest)
    for child in src.iterdir():
        target = dest / child.name
        if child.is_dir():
            shutil.copytree(child, target, dirs_exist_ok=True)
        else:
            shutil.copy2(child, target)


def write_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content)


def remove_if_exists(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def remove_marketplace_kamma() -> None:
    marketplace = HOME / ".agents" / "plugins" / "marketplace.json"
    if not marketplace.exists():
        return
    data = json.loads(marketplace.read_text())
    plugins = data.get("plugins")
    if not isinstance(plugins, list):
        return
    filtered = [plugin for plugin in plugins if plugin.get("name") != "kamma"]
    if filtered == plugins:
        return
    data["plugins"] = filtered
    marketplace.write_text(json.dumps(data, indent=2) + "\n")


def render_toml(command: Command) -> str:
    return (
        f'description = "{command.description}"\n'
        'prompt = """\n'
        f"{command.body}"
        '"""\n'
    )


def render_antigravity_workflow(command: Command) -> str:
    return (
        "---\n"
        f"name: kamma-{command.base}\n"
        f"description: {command.description}\n"
        "---\n\n"
        f"{command.body}"
    )


def render_kilo_skill(command: Command) -> str:
    return (
        "---\n"
        f"name: kamma-{command.base}\n"
        f"description: {command.description}\n"
        "---\n\n"
        f"{command.body}"
    )


def copy_claude(commands: list[Command]) -> None:
    target = HOME / ".claude" / "plugins" / "local" / "kamma"
    ensure_dir(target / "commands" / "kamma")
    ensure_dir(target / ".claude-plugin")
    ensure_dir(target / "skills" / "kamma")
    shutil.copy2(REGISTRATION_DIR / "claude-plugin.json", target / ".claude-plugin" / "plugin.json")
    shutil.copy2(SKILLS_DIR / "kamma" / "SKILL.md", target / "skills" / "kamma" / "SKILL.md")
    for command in commands:
        write_text(target / "commands" / "kamma" / f"{command.base}.toml", render_toml(command))
    copy_tree_contents(TEMPLATES_DIR, target / "templates")


def copy_gemini(commands: list[Command]) -> None:
    target = HOME / ".gemini" / "extensions" / "kamma"
    ensure_dir(target / "commands" / "kamma")
    shutil.copy2(REGISTRATION_DIR / "gemini-extension.json", target / "gemini-extension.json")
    shutil.copy2(REGISTRATION_DIR / "GEMINI.md", target / "GEMINI.md")
    for command in commands:
        write_text(target / "commands" / "kamma" / f"{command.base}.toml", render_toml(command))
    copy_tree_contents(TEMPLATES_DIR, target / "templates")


def copy_antigravity(commands: list[Command]) -> None:
    target = HOME / ".gemini" / "antigravity" / "global_workflows"
    remove_if_exists(HOME / ".gemini" / "antigravity" / "skills" / "kamma")
    ensure_dir(target)
    for old in target.glob("kamma-*.md"):
        old.unlink()
    for command in commands:
        write_text(target / f"kamma-{command.base}.md", render_antigravity_workflow(command))


def copy_opencode(commands: list[Command]) -> None:
    command_target = HOME / ".opencode" / "command"
    ensure_dir(command_target)
    remove_if_exists(command_target / "kamma-status.md")
    for command in commands:
        shutil.copy2(command.source, command_target / f"kamma-{command.base}.md")
    copy_tree_contents(TEMPLATES_DIR, HOME / ".opencode" / "templates" / "kamma")


def copy_codex(commands: list[Command]) -> None:
    prompt_target = HOME / ".codex" / "prompts"
    ensure_dir(prompt_target)
    remove_if_exists(HOME / "plugins" / "kamma")
    remove_marketplace_kamma()
    for command in commands:
        write_text(prompt_target / f"kamma-{command.base}.md", command.body)
    copy_tree_contents(TEMPLATES_DIR, HOME / ".codex" / "templates" / "kamma")


def copy_kilo(commands: list[Command]) -> None:
    skills_root = HOME / ".kilocode" / "skills"
    ensure_dir(skills_root / "kamma")
    for command in commands:
        skill_dir = skills_root / f"kamma-{command.base}"
        ensure_dir(skill_dir)
        write_text(skill_dir / "SKILL.md", render_kilo_skill(command))
    shutil.copy2(SKILLS_DIR / "kamma" / "SKILL.md", skills_root / "kamma" / "SKILL.md")
    copy_tree_contents(TEMPLATES_DIR, HOME / ".kilocode" / "templates" / "kamma")


TARGETS = [
    ("Claude Code", HOME / ".claude", copy_claude),
    ("Gemini CLI", HOME / ".gemini", copy_gemini),
    ("Antigravity", HOME / ".gemini" / "antigravity", copy_antigravity),
    ("OpenCode", HOME / ".opencode", copy_opencode),
    ("Codex CLI", HOME / ".codex", copy_codex),
    ("Kilo CLI", HOME / ".kilocode", copy_kilo),
]


def main() -> None:
    commands = read_commands()
    print(f"Syncing kamma from {ROOT}...")
    for label, root, copier in TARGETS:
        if root.is_dir():
            copier(commands)
            print(f"{label}: copied")
        else:
            print(f"{label}: skipped")


if __name__ == "__main__":
    main()
