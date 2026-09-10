#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from rich import print


ROOT = Path(__file__).resolve().parent.parent
COMMANDS_DIR = ROOT / "commands"
TEMPLATES_DIR = ROOT / "templates"
REGISTRATION_DIR = ROOT / "registration"
SKILLS_DIR = ROOT / "skills"
HOOKS_DIR = ROOT / "hooks"
HOOK_MARKER = "kamma_gate.py"


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
        *(
            Path(os.environ[name])
            for name in ("HOME", "USERPROFILE")
            if os.environ.get(name)
        ),
    ]
)
APPDATA_DIRS = unique_paths(
    [
        *(
            Path(os.environ[name])
            for name in ("APPDATA", "LOCALAPPDATA")
            if os.environ.get(name)
        ),
    ]
)
AGENTS_DIRS = unique_paths([home / ".agents" for home in HOME_DIRS])


def existing(paths: list[Path]) -> list[Path]:
    return [path for path in unique_paths(paths) if path.is_dir()]


def antigravity_roots() -> list[Path]:
    roots: list[Path] = []
    for home in HOME_DIRS:
        gemini = home / ".gemini"
        if (gemini / "antigravity").is_dir() or (gemini / "antigravity-cli").is_dir():
            roots.append(gemini)
    return unique_paths(roots)


def read_commands() -> list[Command]:
    commands: list[Command] = []
    for path in sorted(COMMANDS_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
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
    path.write_text(content, encoding="utf-8")


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
        data = json.loads(marketplace.read_text(encoding="utf-8"))
        plugins = data.get("plugins")
        if not isinstance(plugins, list):
            continue
        filtered = [plugin for plugin in plugins if plugin.get("name") != "kamma"]
        if filtered == plugins:
            continue
        data["plugins"] = filtered
        marketplace.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def render_toml(command: Command) -> str:
    return f'description = "{command.description}"\nprompt = """\n{command.body}"""\n'


def render_markdown_frontmatter(command: Command) -> str:
    return (
        "---\n"
        f"name: kamma-{command.base}\n"
        f"description: {command.description}\n"
        "---\n\n"
        f"{command.body}"
    )


def render_antigravity_workflow(command: Command) -> str:
    return f"---\ndescription: {command.description}\n---\n\n{command.body}"


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


def is_venv_interpreter(path: Path) -> bool:
    """True if ``path`` lives inside a virtualenv (has a pyvenv.cfg sibling).

    ``sync.py`` normally runs under ``uv run``, which puts the repo's disposable
    ``.venv/bin`` first on PATH — so a plain ``shutil.which("python3")`` picks up
    a python that moves or disappears on the next ``uv sync``. A hook needs a
    stable, always-present interpreter, not whatever happened to be first on
    PATH at sync time.
    """
    return (path.parent.parent / "pyvenv.cfg").is_file()


def resolve_hook_interpreter() -> str:
    for candidate in ("/usr/bin/python3", "/usr/local/bin/python3", "/bin/python3"):
        if Path(candidate).is_file():
            return candidate
    which_result = shutil.which("python3")
    if which_result and not is_venv_interpreter(Path(which_result)):
        return which_result
    return sys.executable


def install_kamma_gate_hooks(root: Path) -> None:
    """Copy the gate script into ``root`` and merge its hooks into settings.json.

    Reads existing settings (or starts from ``{}``), never overwrites unrelated
    keys, backs up the file once before the first write, and de-duplicates any
    prior kamma entries by matching on ``HOOK_MARKER`` so repeat syncs are
    idempotent.
    """
    hooks_target = root / "hooks"
    ensure_dir(hooks_target)
    script_dest = hooks_target / "kamma_gate.py"
    shutil.copy2(HOOKS_DIR / "kamma_gate.py", script_dest)

    interpreter = resolve_hook_interpreter()
    command_prefix = f"{shlex.quote(interpreter)} {shlex.quote(str(script_dest))}"

    settings_path = root / "settings.json"
    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            settings = {}
    else:
        settings = {}
    if not isinstance(settings, dict):
        settings = {}

    if settings_path.exists():
        backup_path = settings_path.with_suffix(settings_path.suffix + ".bak")
        if not backup_path.exists():
            shutil.copy2(settings_path, backup_path)

    hooks_config = settings.get("hooks")
    if not isinstance(hooks_config, dict):
        hooks_config = {}
    settings["hooks"] = hooks_config

    def strip_kamma_entries(entries: object) -> list:
        if not isinstance(entries, list):
            return []
        kept = []
        for entry in entries:
            handlers = entry.get("hooks", []) if isinstance(entry, dict) else []
            if not isinstance(handlers, list):
                handlers = []
            if any(
                isinstance(h, dict) and HOOK_MARKER in str(h.get("command", ""))
                for h in handlers
            ):
                continue
            kept.append(entry)
        return kept

    pre_tool_use = strip_kamma_entries(hooks_config.get("PreToolUse"))
    pre_tool_use.append(
        {
            "matcher": "Edit|Write|NotebookEdit",
            "hooks": [{"type": "command", "command": f"{command_prefix} spec-gate"}],
        }
    )
    hooks_config["PreToolUse"] = pre_tool_use

    stop = strip_kamma_entries(hooks_config.get("Stop", []))
    stop.append(
        {
            "hooks": [{"type": "command", "command": f"{command_prefix} stop-gate"}],
        }
    )
    hooks_config["Stop"] = stop

    settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")


def sync_claude(root: Path, commands: list[Command]) -> None:
    target = root / "commands" / "kamma"
    remove_stale(
        [
            target / "status.md",
            target / "kamma-status.md",
            target / "one-shot.md",
        ]
    )
    ensure_dir(target)
    for command in commands:
        if command.base == "kamma":
            shutil.copy2(command.source, root / "commands" / "kamma.md")
        else:
            shutil.copy2(command.source, target / f"{command.base}.md")
    install_kamma_gate_hooks(root)


def sync_antigravity(root: Path, commands: list[Command]) -> None:
    """Install Kamma into Antigravity from the ``~/.gemini`` root.

    Skills are the primary integration and are read by both the Antigravity IDE
    and the ``agy`` CLI (whose ``/`` menu lists skills, not workflows):
    ``~/.gemini/skills/kamma`` is the single-run orchestrator and
    ``~/.gemini/skills/kamma-<step>`` exposes each step as its own ``/kamma-*``
    entry. Global workflows under ``~/.gemini/antigravity/global_workflows`` add
    the same ``/kamma-*`` slash commands in the IDE.
    """
    skills_root = root / "skills"
    skill_target = skills_root / "kamma"
    workflows_target = root / "antigravity" / "global_workflows"

    remove_if_exists(root / "antigravity" / "skills" / "kamma")
    remove_if_exists(skill_target / "templates")
    remove_stale(
        [
            workflows_target / "kamma-status.md",
            workflows_target / "status.md",
        ]
    )
    for old in skills_root.glob("kamma-*"):
        remove_if_exists(old)

    ensure_dir(skill_target)
    shutil.copy2(SKILLS_DIR / "kamma" / "SKILL.md", skill_target / "SKILL.md")
    for command in commands:
        if command.base == "kamma":
            continue
        step_dir = skills_root / f"kamma-{command.base}"
        write_text(step_dir / "SKILL.md", render_markdown_frontmatter(command))
        if command.base == "0-setup":
            copy_tree_contents(TEMPLATES_DIR, step_dir / "templates")

    ensure_dir(workflows_target)
    for old in workflows_target.glob("kamma-*.md"):
        old.unlink()
    for command in commands:
        name = "kamma" if command.base == "kamma" else f"kamma-{command.base}"
        write_text(
            workflows_target / f"{name}.md", render_antigravity_workflow(command)
        )


def sync_opencode(root: Path, commands: list[Command]) -> None:
    command_target = resolve_opencode_command_dir(root)
    ensure_dir(command_target)
    remove_stale(
        [
            command_target / "kamma-status.md",
            command_target / "status.md",
            command_target / "kamma-one-shot.md",
            command_target / "kamma-kamma.md",
        ]
    )
    for command in commands:
        if command.base == "kamma":
            shutil.copy2(command.source, command_target / "kamma.md")
        else:
            shutil.copy2(command.source, command_target / f"kamma-{command.base}.md")
    copy_tree_contents(TEMPLATES_DIR, root / "templates" / "kamma")


def sync_codex(root: Path, commands: list[Command]) -> None:
    if not any(command.base == "kamma" for command in commands):
        raise ValueError("Codex sync requires the kamma command")

    prompt_target = root / "prompts"
    skills_root = root / "skills"
    ensure_dir(prompt_target)
    remove_stale(
        [
            prompt_target / "kamma-status.md",
            prompt_target / "status.md",
            prompt_target / "kamma-one-shot.md",
        ]
    )
    remove_if_exists(skills_root / "kamma")
    for old in skills_root.glob("kamma-*"):
        remove_if_exists(old)
    for old in prompt_target.glob("kamma-*.md"):
        old.unlink()
    remove_if_exists(root.parent / "plugins" / "kamma")
    remove_marketplace_kamma()
    for command in commands:
        write_text(prompt_target / f"kamma-{command.base}.md", command.body)

    skill_target = skills_root / "kamma"
    ensure_dir(skill_target)
    shutil.copy2(SKILLS_DIR / "kamma" / "SKILL.md", skill_target / "SKILL.md")
    for command in commands:
        if command.base == "kamma":
            continue
        write_text(
            skills_root / f"kamma-{command.base}" / "SKILL.md",
            render_markdown_frontmatter(command),
        )

    copy_tree_contents(TEMPLATES_DIR, root / "templates" / "kamma")


def sync_qwen(root: Path, commands: list[Command]) -> None:
    target = root / "extensions" / "kamma"
    remove_stale(
        [
            target / "commands" / "kamma" / "status.toml",
            target / "commands" / "kamma" / "kamma-status.toml",
        ]
    )
    ensure_dir(target / "commands" / "kamma")
    shutil.copy2(
        REGISTRATION_DIR / "qwen-extension.json", target / "qwen-extension.json"
    )
    shutil.copy2(REGISTRATION_DIR / "QWEN.md", target / "QWEN.md")
    for command in commands:
        write_text(
            target / "commands" / "kamma" / f"{command.base}.toml", render_toml(command)
        )
    copy_tree_contents(TEMPLATES_DIR, target / "templates")


def sync_pi(root: Path, commands: list[Command]) -> None:
    prompts_target = root / "prompts"
    skills_root = root / "skills"

    ensure_dir(prompts_target)
    for old in prompts_target.glob("kamma*.md"):
        old.unlink()
    remove_if_exists(skills_root / "kamma")
    for old in skills_root.glob("kamma-*"):
        remove_if_exists(old)

    for command in commands:
        name = "kamma" if command.base == "kamma" else f"kamma-{command.base}"
        write_text(
            prompts_target / f"{name}.md",
            render_antigravity_workflow(command),
        )

    skill_target = skills_root / "kamma"
    ensure_dir(skill_target)
    shutil.copy2(SKILLS_DIR / "kamma" / "SKILL.md", skill_target / "SKILL.md")
    for command in commands:
        if command.base == "kamma":
            continue
        step_dir = skills_root / f"kamma-{command.base}"
        write_text(step_dir / "SKILL.md", render_markdown_frontmatter(command))
        if command.base == "0-setup":
            copy_tree_contents(TEMPLATES_DIR, step_dir / "templates")


def sync_kilo(root: Path, commands: list[Command]) -> None:
    skills_root = root / "skills"
    remove_stale(
        [
            skills_root / "kamma-status",
            skills_root / "status",
            skills_root / "kamma-one-shot",
            skills_root / "kamma-kamma",
        ]
    )
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


def get_targets(create: bool) -> list[Target]:
    if create:
        return [
            Target(
                "Claude Code", unique_paths([home / ".claude" for home in HOME_DIRS])
            ),
            Target(
                "Antigravity", unique_paths([home / ".gemini" for home in HOME_DIRS])
            ),
            Target(
                "OpenCode",
                unique_paths(
                    [
                        *(home / ".opencode" for home in HOME_DIRS),
                        *(home / ".config" / "opencode" for home in HOME_DIRS),
                        *(app_dir / "opencode" for app_dir in APPDATA_DIRS),
                    ]
                ),
            ),
            Target("Codex CLI", unique_paths([home / ".codex" for home in HOME_DIRS])),
            Target(
                "Kilo CLI", unique_paths([home / ".kilocode" for home in HOME_DIRS])
            ),
            Target("Pi", unique_paths([home / ".pi" / "agent" for home in HOME_DIRS])),
            Target("Qwen Code", unique_paths([home / ".qwen" for home in HOME_DIRS])),
        ]
    else:
        return [
            Target("Claude Code", existing([home / ".claude" for home in HOME_DIRS])),
            Target("Antigravity", antigravity_roots()),
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
            Target("Pi", existing([home / ".pi" / "agent" for home in HOME_DIRS])),
            Target("Qwen Code", existing([home / ".qwen" for home in HOME_DIRS])),
        ]


SYNCERS = {
    "Claude Code": sync_claude,
    "Antigravity": sync_antigravity,
    "OpenCode": sync_opencode,
    "Codex CLI": sync_codex,
    "Kilo CLI": sync_kilo,
    "Pi": sync_pi,
    "Qwen Code": sync_qwen,
}


COMMAND_PREFIX: dict[str, str] = {
    "Codex CLI": "$kamma",
    "Antigravity": "/kamma",
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync kamma commands to local AI tool directories."
    )
    parser.add_argument(
        "--create",
        action="store_true",
        help="Create target directories even if they do not exist.",
    )
    args = parser.parse_args()

    commands = read_commands()
    errors: list[str] = []
    synced_labels: list[str] = []
    targets = get_targets(args.create)

    print(f"\n[bold]Syncing kamma[/bold] [dim]from {ROOT}[/dim]\n")
    for target in targets:
        if not target.roots:
            print(f"  [dim]\\[-] {target.label} skipped[/dim]")
            continue
        syncer = SYNCERS[target.label]
        try:
            for root in target.roots:
                if args.create:
                    ensure_dir(root)
                syncer(root, commands)
            print(f"  [green]\\[+][/green] {target.label}")
            synced_labels.append(target.label)
        except Exception as exc:
            errors.append(f"{target.label}: {exc}")
            print(f"  [red]\\[!] {target.label} {exc}[/red]")
    copied = len([t for t in targets if t.roots]) - len(errors)
    skipped = len([t for t in targets if not t.roots])
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
