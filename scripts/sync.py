#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from rich import print


ROOT = Path(__file__).resolve().parent.parent
COMMANDS_DIR = ROOT / "commands"
TEMPLATES_DIR = ROOT / "templates"
REGISTRATION_DIR = ROOT / "registration"
SKILLS_DIR = ROOT / "skills"


@dataclass(frozen=True)
class Command:
    base: str
    description: str
    body: str
    source: Path


@dataclass(frozen=True)
class Target:
    label: str
    roots: list[Path]


def unique_paths(paths: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    ordered: list[Path] = []
    for path in paths:
        resolved = path.expanduser()
        if resolved in seen:
            continue
        seen.add(resolved)
        ordered.append(resolved)
    return ordered


HOME_DIRS = unique_paths(
    [
        Path.home(),
        *(Path(os.environ[name]) for name in ("HOME", "USERPROFILE") if os.environ.get(name)),
    ]
)
APPDATA_DIRS = unique_paths(
    [
        *(Path(os.environ[name]) for name in ("APPDATA", "LOCALAPPDATA") if os.environ.get(name)),
    ]
)
AGENTS_DIRS = unique_paths([home / ".agents" for home in HOME_DIRS])


def existing(paths: list[Path]) -> list[Path]:
    return [path for path in unique_paths(paths) if path.is_dir()]


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


def remove_stale(paths: list[Path]) -> None:
    for path in paths:
        remove_if_exists(path)


def remove_marketplace_kamma() -> None:
    for agents_dir in AGENTS_DIRS:
        marketplace = agents_dir / "plugins" / "marketplace.json"
        if not marketplace.exists():
            continue
        data = json.loads(marketplace.read_text())
        plugins = data.get("plugins")
        if not isinstance(plugins, list):
            continue
        filtered = [plugin for plugin in plugins if plugin.get("name") != "kamma"]
        if filtered == plugins:
            continue
        data["plugins"] = filtered
        marketplace.write_text(json.dumps(data, indent=2) + "\n")


def render_toml(command: Command) -> str:
    return (
        f'description = "{command.description}"\n'
        'prompt = """\n'
        f"{command.body}"
        '"""\n'
    )


def render_markdown_frontmatter(command: Command) -> str:
    return (
        "---\n"
        f"name: kamma-{command.base}\n"
        f"description: {command.description}\n"
        "---\n\n"
        f"{command.body}"
    )


def resolve_opencode_command_dir(root: Path) -> Path:
    commands_dir = root / "commands"
    command_dir = root / "command"
    if commands_dir.exists() and not command_dir.exists():
        return commands_dir
    if command_dir.exists() and not commands_dir.exists():
        return command_dir
    if root.name == ".opencode":
        return command_dir
    return commands_dir


def sync_claude(root: Path, commands: list[Command]) -> None:
    target = root / "commands" / "kamma"
    remove_stale([
        target / "status.md",
        target / "kamma-status.md",
        target / "one-shot.md",
    ])
    ensure_dir(target)
    for command in commands:
        if command.base == "kamma":
            shutil.copy2(command.source, root / "commands" / "kamma.md")
        else:
            shutil.copy2(command.source, target / f"{command.base}.md")


def sync_gemini(root: Path, commands: list[Command]) -> None:
    target = root / "extensions" / "kamma"
    remove_stale([
        target / "commands" / "kamma" / "status.toml",
        target / "commands" / "kamma" / "kamma-status.toml",
        root / "commands" / "kamma" / "status.toml",
        root / "commands" / "kamma" / "kamma-status.toml",
        target / "commands" / "kamma" / "one-shot.toml",
    ])
    ensure_dir(target / "commands" / "kamma")
    shutil.copy2(REGISTRATION_DIR / "gemini-extension.json", target / "gemini-extension.json")
    shutil.copy2(REGISTRATION_DIR / "GEMINI.md", target / "GEMINI.md")
    for command in commands:
        write_text(target / "commands" / "kamma" / f"{command.base}.toml", render_toml(command))
    copy_tree_contents(TEMPLATES_DIR, target / "templates")


def sync_antigravity(root: Path, commands: list[Command]) -> None:
    target = root / "global_workflows"
    remove_if_exists(root / "skills" / "kamma")
    remove_stale([
        target / "kamma-status.md",
        target / "status.md",
    ])
    ensure_dir(target)
    for old in target.glob("kamma-*.md"):
        old.unlink()
    for command in commands:
        write_text(target / f"kamma-{command.base}.md", render_markdown_frontmatter(command))


def sync_opencode(root: Path, commands: list[Command]) -> None:
    command_target = resolve_opencode_command_dir(root)
    ensure_dir(command_target)
    remove_stale([
        command_target / "kamma-status.md",
        command_target / "status.md",
        command_target / "kamma-one-shot.md",
        command_target / "kamma-kamma.md",
    ])
    for command in commands:
        if command.base == "kamma":
            shutil.copy2(command.source, command_target / "kamma.md")
        else:
            shutil.copy2(command.source, command_target / f"kamma-{command.base}.md")
    copy_tree_contents(TEMPLATES_DIR, root / "templates" / "kamma")


def sync_codex(root: Path, commands: list[Command]) -> None:
    prompt_target = root / "prompts"
    ensure_dir(prompt_target)
    remove_stale([
        prompt_target / "kamma-status.md",
        prompt_target / "status.md",
        prompt_target / "kamma-one-shot.md",
    ])
    remove_if_exists(root.parent / "plugins" / "kamma")
    remove_marketplace_kamma()
    for command in commands:
        write_text(prompt_target / f"kamma-{command.base}.md", command.body)
    copy_tree_contents(TEMPLATES_DIR, root / "templates" / "kamma")


def sync_kilo(root: Path, commands: list[Command]) -> None:
    skills_root = root / "skills"
    remove_stale([
        skills_root / "kamma-status",
        skills_root / "status",
        skills_root / "kamma-one-shot",
        skills_root / "kamma-kamma",
    ])
    ensure_dir(skills_root / "kamma")
    for command in commands:
        if command.base == "kamma":
            write_text(
                skills_root / "kamma" / "SKILL.md",
                "---\n"
                "name: kamma\n"
                f"description: {command.description}\n"
                "---\n\n"
                f"{command.body}",
            )
        else:
            skill_dir = skills_root / f"kamma-{command.base}"
            ensure_dir(skill_dir)
            write_text(skill_dir / "SKILL.md", render_markdown_frontmatter(command))
    copy_tree_contents(TEMPLATES_DIR, root / "templates" / "kamma")


TARGETS = [
    Target("Claude Code", existing([home / ".claude" for home in HOME_DIRS])),
    Target("Gemini CLI", existing([home / ".gemini" for home in HOME_DIRS])),
    Target("Antigravity", existing([home / ".gemini" / "antigravity" for home in HOME_DIRS])),
    Target(
        "OpenCode",
        existing(
            [
                *(home / ".opencode" for home in HOME_DIRS),
                *(home / ".config" / "opencode" for home in HOME_DIRS),
                *(app_dir / "opencode" for app_dir in APPDATA_DIRS),
            ]
        ),
    ),
    Target("Codex CLI", existing([home / ".codex" for home in HOME_DIRS])),
    Target("Kilo CLI", existing([home / ".kilocode" for home in HOME_DIRS])),
]
SYNCERS = {
    "Claude Code": sync_claude,
    "Gemini CLI": sync_gemini,
    "Antigravity": sync_antigravity,
    "OpenCode": sync_opencode,
    "Codex CLI": sync_codex,
    "Kilo CLI": sync_kilo,
}


COMMAND_PREFIX: dict[str, str] = {
    "Codex CLI": "$kamma",
}


def main() -> None:
    commands = read_commands()
    errors: list[str] = []
    synced_labels: list[str] = []
    print(f"\n[bold]Syncing kamma[/bold] [dim]from {ROOT}[/dim]\n")
    for target in TARGETS:
        if not target.roots:
            print(f"  [dim]\\[-] {target.label} skipped[/dim]")
            continue
        syncer = SYNCERS[target.label]
        try:
            for root in target.roots:
                syncer(root, commands)
            print(f"  [green]\\[+][/green] {target.label}")
            synced_labels.append(target.label)
        except Exception as exc:
            errors.append(f"{target.label}: {exc}")
            print(f"  [red]\\[!] {target.label} {exc}[/red]")
    copied = len([t for t in TARGETS if t.roots]) - len(errors)
    skipped = len([t for t in TARGETS if not t.roots])
    summary = f"\n[bold]{copied} copied[/bold], [dim]{skipped} skipped[/dim]"
    if errors:
        summary += f", [red]{len(errors)} failed[/red]"
    print(summary)

    if synced_labels:
        print("\n[bold]To use kamma:[/bold]")
        for label in synced_labels:
            prefix = COMMAND_PREFIX.get(label, "/kamma")
            print(f"  [cyan]{label}:[/cyan]  {prefix}")

    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
