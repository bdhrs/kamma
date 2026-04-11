import json
import subprocess

import typer
from rich.table import Table

from kammika.config import KammikaConfig
from kammika.paths import config_path, kamma_dir, target_repo_root
from kammika.ui import (
    console,
    error,
    info,
    muted,
    prompt_confirm,
    prompt_text,
    show_banner,
    success,
    warning,
)

INIT_BANNER = """

▄▄                             ▀▀  ▄▄             ▀▀        ▀▀  ██
██ ▄█▀  ▀▀█▄ ███▄███▄ ███▄███▄ ██  ██ ▄█▀  ▀▀█▄   ██  ████▄ ██ ▀██▀▀
████   ▄█▀██ ██ ██ ██ ██ ██ ██ ██  ████   ▄█▀██   ██  ██ ██ ██  ██
██ ▀█▄ ▀█▄██ ██ ██ ██ ██ ██ ██ ██▄ ██ ▀█▄ ▀█▄██   ██▄ ██ ██ ██▄ ██

"""


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True)


def _detect_repo_slug() -> str | None:
    result = _run(["gh", "repo", "view", "--json", "nameWithOwner"])
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)["nameWithOwner"]
        except (json.JSONDecodeError, KeyError):
            pass
    return None


def _detect_projects(owner: str) -> list[dict] | None:
    """Return list of {number, title} dicts for the owner's projects, or None on failure."""
    result = _run(
        ["gh", "project", "list", "--owner", owner, "--format", "json", "--limit", "50"]
    )
    if result.returncode != 0:
        if "unknown owner type" in result.stderr:
            warning(
                "Could not list GitHub projects — token is missing the 'read:project' scope.\n"
                "If GITHUB_TOKEN is set in your environment, update that token's scopes at "
                "https://github.com/settings/tokens\n"
                "Otherwise run: gh auth refresh -s read:project"
            )
        return None
    try:
        raw = json.loads(result.stdout)
        items = raw if isinstance(raw, list) else raw.get("projects", [])
        return [
            {"number": str(p.get("number", "")), "title": p.get("title", "")}
            for p in items
            if p.get("number")
        ]
    except (json.JSONDecodeError, AttributeError):
        return None


def _parse_project_ref(raw: str) -> str:
    """Normalise a GitHub Project URL or owner/number to 'owner/number'."""
    raw = raw.strip()
    if raw.startswith("https://"):
        parts = raw.rstrip("/").split("/")
        try:
            orgs_idx = parts.index("orgs")
            owner = parts[orgs_idx + 1]
            number = parts[-1]
            return f"{owner}/{number}"
        except (ValueError, IndexError):
            pass
    return raw


def _confirm(message: str, default: bool = True) -> bool:
    return prompt_confirm(message, default=default)


def _choose_repo(current: str | None = None) -> str:
    if current:
        if _confirm(f"This is your GitHub repo: {current}. Is that correct?"):
            return current

    detected = _detect_repo_slug()
    if detected:
        if _confirm(f"This is your GitHub repo: {detected}. Is that correct?"):
            return detected

    warning("Please enter the GitHub repo manually.")
    return prompt_text("GitHub repo (owner/name)")


def _prompt_project_url() -> str:
    raw = prompt_text(
        "Do you have a GitHub Project? Paste the URL (or press Enter to continue without one)",
        default="",
    )
    if not raw.strip():
        return ""
    return _parse_project_ref(raw.strip())


def _pick_project(owner: str) -> str:
    """Auto-select one project, choose from many, or prompt for an optional URL."""
    projects = _detect_projects(owner)

    if projects and len(projects) == 1:
        p = projects[0]
        ref = f"{owner}/{p['number']}"
        if _confirm(f"This is your GitHub project: {ref}. Is that correct?"):
            return ref
        return _prompt_project_url()

    if projects and len(projects) > 1:
        table = Table(show_header=True, header_style="question")
        table.add_column("#", style="question", width=4)
        table.add_column("Project")
        table.add_column("Number", style="muted")
        for i, project in enumerate(projects, 1):
            table.add_row(str(i), project["title"], project["number"])
        console.print()
        console.print(table)
        console.print()

        while True:
            choice = prompt_text(f"Pick a project [1-{len(projects)}]")
            try:
                idx = int(choice) - 1
            except ValueError:
                idx = -1
            if 0 <= idx < len(projects):
                project = projects[idx]
                ref = f"{owner}/{project['number']}"
                success(f"Selected: {project['title']} ({ref})")
                return ref
            warning(f"Enter a number between 1 and {len(projects)}.")

    return _prompt_project_url()


def _choose_project(owner: str, current: str | None = None) -> str:
    if current is not None:
        label = current or "none"
        if _confirm(f"This is your GitHub project: {label}. Is that correct?"):
            return current
    return _pick_project(owner)


def run_init(show_next: bool = True) -> None:
    show_banner(INIT_BANNER)

    try:
        repo_root = target_repo_root()
    except RuntimeError as exc:
        error(f"Error: {exc}")
        raise typer.Exit(1)

    muted(f"Repo root: {repo_root}")

    cfg_path = config_path()
    existing_config: KammikaConfig | None = None
    if cfg_path.exists():
        try:
            existing_config = KammikaConfig.from_dict(json.loads(cfg_path.read_text()))
            muted(f"Existing config found: {cfg_path}")
        except (json.JSONDecodeError, KeyError, TypeError):
            warning("Existing config is invalid. Reconfiguring.")

    repo_slug = _choose_repo(existing_config.repo if existing_config else None)

    owner = repo_slug.split("/")[0]
    project_ref = _choose_project(
        owner, existing_config.project if existing_config else None
    )

    kamma = kamma_dir()
    missing = [
        f for f in ["tech.md", "workflow.md", "project.md"] if not (kamma / f).exists()
    ]
    if missing:
        error(
            f"Missing kamma files: {', '.join(missing)}. Run `/kamma:0-setup` in this repo first."
        )
        raise typer.Exit(1)

    config = KammikaConfig(repo=repo_slug, project=project_ref)
    cfg_path.write_text(json.dumps(config.to_dict(), indent=2) + "\n")
    success(f"Config written to {cfg_path}")
    success("kammika init complete.")
    if show_next:
        info("Next: Run `kammika run`.")
