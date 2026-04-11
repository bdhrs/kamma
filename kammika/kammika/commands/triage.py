import json
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import typer

from kammika.agents import describe_agent, get_agent_model
from kammika.config import KammikaConfig
from kammika.paths import config_path, kamma_dir, queue_path, target_repo_root
from kammika.ui import console, error, muted, show_banner, success, warning, warm_panel

CLAUDE_MODEL = "opus"
OPENCODE_MODEL = "openai/gpt-5.4"

TRIAGE_BANNER = """

 ██         ▀▀
▀██▀▀ ████▄ ██   ▀▀█▄ ▄████ ▄█▀█▄
 ██   ██ ▀▀ ██  ▄█▀██ ██ ██ ██▄█▀
 ██   ██    ██▄ ▀█▄██ ▀████ ▀█▄▄▄
                         ██
                       ▀▀▀

"""

_BLOCKED_STATUSES = {"in progress", "done", "blocked"}
_PRIORITY_RANK = {"p0": 0, "p1": 1, "p2": 2, "p3": 3, "p4": 4}


@dataclass
class Candidate:
    number: int
    title: str
    body: str
    labels: list[str] = field(default_factory=list)
    created_at: str = ""
    status: str = ""
    age_days: int = 0

    @property
    def priority_rank(self) -> int:
        for label in self.labels:
            if label.lower() in _PRIORITY_RANK:
                return _PRIORITY_RANK[label.lower()]
        return 5

    @property
    def is_bug(self) -> bool:
        return any(l.lower() == "bug" for l in self.labels)


_NETWORK_ERRORS = ("TLS handshake timeout", "connection refused", "no such host", "i/o timeout", "dial tcp")
_RETRY_ATTEMPTS = 3
_RETRY_DELAY = 4  # seconds


def _run(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True, cwd=cwd)


def _run_with_retry(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run a command, retrying up to _RETRY_ATTEMPTS times on transient network errors."""
    import time

    last: subprocess.CompletedProcess | None = None
    for attempt in range(1, _RETRY_ATTEMPTS + 1):
        result = _run(args, cwd=cwd)
        if result.returncode == 0:
            return result
        stderr = result.stderr.lower()
        if any(err in stderr for err in _NETWORK_ERRORS):
            if attempt < _RETRY_ATTEMPTS:
                muted(f"Network error, retrying ({attempt}/{_RETRY_ATTEMPTS - 1})...")
                time.sleep(_RETRY_DELAY)
                last = result
                continue
        return result
    return last  # type: ignore[return-value]


def _load_config() -> KammikaConfig:
    path = config_path()
    if not path.exists():
        error("kamma/kammika.config.json not found. Run `kammika init` first.")
        raise typer.Exit(1)
    return KammikaConfig.from_dict(json.loads(path.read_text()))


def _fetch_issues(repo: str) -> list[Candidate]:
    result = _run_with_retry(
        [
            "gh",
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            "open",
            "--json",
            "number,title,body,labels,createdAt",
            "--limit",
            "200",
        ]
    )
    if result.returncode != 0:
        warning(f"Could not fetch issues: {result.stderr.strip()}")
        return []
    try:
        raw = json.loads(result.stdout)
    except json.JSONDecodeError:
        warning("Could not parse issue list JSON.")
        return []

    candidates = []
    for item in raw:
        try:
            number = int(item["number"])
            title = str(item.get("title", ""))
            body = str(item.get("body", "") or "")
            labels = [
                lbl["name"]
                for lbl in item.get("labels", [])
                if isinstance(lbl, dict) and "name" in lbl
            ]
            created_at = str(item.get("createdAt", ""))
            age_days = _age_days(created_at)
            candidates.append(
                Candidate(
                    number=number,
                    title=title,
                    body=body,
                    labels=labels,
                    created_at=created_at,
                    age_days=age_days,
                )
            )
        except (KeyError, ValueError, TypeError):
            continue
    return candidates


def _fetch_project_items(owner: str, number: str) -> dict[int, str]:
    """Returns {issue_number: status} for all project items that link to issues."""
    result = _run_with_retry(
        [
            "gh",
            "project",
            "item-list",
            number,
            "--owner",
            owner,
            "--format",
            "json",
            "--limit",
            "200",
        ]
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        if "unknown owner type" in stderr:
            warning(
                "Could not fetch GitHub project items — token is missing the 'read:org' scope.\n"
                "(gh surfaces this as the opaque error 'unknown owner type'.)\n"
                "If GITHUB_TOKEN is set in your environment, add 'read:org' to that token at "
                "https://github.com/settings/tokens\n"
                "Otherwise run: gh auth refresh -s read:org"
            )
        else:
            warning(f"Could not fetch project items: {stderr}")
        return {}
    try:
        raw = json.loads(result.stdout)
    except json.JSONDecodeError:
        warning("Could not parse project items JSON.")
        return {}

    items = raw if isinstance(raw, list) else raw.get("items", [])
    status_map: dict[int, str] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        issue_number = _extract_issue_number(item)
        if issue_number is None:
            continue
        status = _extract_status(item)
        status_map[issue_number] = status
    return status_map


def _extract_issue_number(item: dict) -> int | None:
    for key in ("content", "linkedContent"):
        content = item.get(key)
        if isinstance(content, dict):
            for nk in ("number", "issueNumber"):
                if isinstance(content.get(nk), int):
                    return content[nk]
    for key in ("number", "issueNumber"):
        if isinstance(item.get(key), int):
            return item[key]
    return None


def _extract_status(item: dict) -> str:
    for key in ("status", "Status"):
        val = item.get(key)
        if isinstance(val, str) and val:
            return val
    field_values = item.get("fieldValues", [])
    if isinstance(field_values, list):
        for fv in field_values:
            if not isinstance(fv, dict):
                continue
            if fv.get("field", {}).get("name", "").lower() == "status":
                return str(fv.get("value", ""))
    return ""


def _age_days(created_at: str) -> int:
    if not created_at:
        return 0
    try:
        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).days
    except ValueError:
        return 0


def _claimed_issue_numbers() -> set[int]:
    claimed: set[int] = set()
    kamma = kamma_dir()
    for spec_path in kamma.glob("threads/*/spec.md"):
        text = spec_path.read_text()
        for line in text.splitlines()[:20]:
            m = re.search(r"#(\d+)", line)
            if m:
                claimed.add(int(m.group(1)))
                break
    return claimed


def rank(candidates: list[Candidate]) -> list[Candidate]:
    """Sort candidates by (priority_rank, not_is_bug, age descending)."""
    return sorted(
        candidates, key=lambda c: (c.priority_rank, not c.is_bug, -c.age_days)
    )


def _extract_chosen(text: str) -> dict | None:
    """Extract a {"chosen": N, ...} object from potentially noisy LLM output."""
    text = text.strip()
    # Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Strip markdown code fences
    cleaned = re.sub(r"```(?:json)?\s*", "", text).replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    # Find the first {...} block that contains "chosen"
    for m in re.finditer(r"\{[^{}]+\}", text, re.DOTALL):
        try:
            obj = json.loads(m.group())
            if "chosen" in obj:
                return obj
        except json.JSONDecodeError:
            continue
    return None


def _llm_pick(candidates: list[Candidate], agents: list[str], models: dict[str, str] | None = None) -> int | None:
    top = candidates[:20]
    payload = [
        {
            "number": c.number,
            "title": c.title,
            "body_excerpt": c.body[:500],
            "labels": c.labels,
            "age_days": c.age_days,
            "status": c.status,
        }
        for c in top
    ]
    prompt = (
        "You are helping prioritise GitHub issues. "
        "Pick the single most important item to work on next. "
        "Prefer bugs over features, prefer P0→P4 priority labels, prefer older items when tied. "
        'Return ONLY a JSON object: {"chosen": <number>, "rationale": "<text>"}.\n\n'
        f"Candidates:\n{json.dumps(payload)}"
    )

    valid_numbers = {c.number for c in top}
    for agent in agents:
        if agent == "claude":
            cmd = [
                "claude",
                "-p",
                prompt,
                "--model",
                get_agent_model("claude", models) or CLAUDE_MODEL,
                "--output-format",
                "json",
            ]
        elif agent == "opencode":
            cmd = [
                "opencode",
                "run",
                prompt,
                "--model",
                get_agent_model("opencode", models) or OPENCODE_MODEL,
                "--format",
                "json",
            ]
        else:
            continue

        result = _run(cmd)
        if result.returncode != 0:
            muted(
                f"Recommendation via {describe_agent(agent, models)} failed "
                f"(exit {result.returncode}), trying next."
            )
            continue

        try:
            raw = json.loads(result.stdout)
            # Unwrap Claude Code's {"result": "..."} envelope
            if isinstance(raw, dict) and "result" in raw:
                inner = raw["result"]
                text = inner if isinstance(inner, str) else json.dumps(inner)
            else:
                text = json.dumps(raw)
            obj = _extract_chosen(text)
            if obj is not None:
                chosen = int(obj["chosen"])
                if chosen in valid_numbers:
                    return chosen
        except (json.JSONDecodeError, KeyError, ValueError, TypeError):
            pass

        muted(
            f"Recommendation via {describe_agent(agent, models)} returned "
            "unparseable output, trying next."
        )

    return None


def _parse_project_ref(project: str) -> tuple[str, str]:
    """Split 'owner/number' into (owner, number)."""
    parts = project.split("/", 1)
    if len(parts) != 2:
        raise ValueError(
            f"Cannot parse project ref '{project}'. Expected 'owner/number'."
        )
    return parts[0], parts[1]


def get_candidates(config: "KammikaConfig") -> list[Candidate]:
    """Fetch, filter, deduplicate, and rank all open issues."""
    repo = config.repo

    muted(f"Looking for open issues in {repo}.")
    issue_candidates = _fetch_issues(repo)
    muted(f"Found {len(issue_candidates)} open issues.")

    project_status: dict[int, str] = {}
    if config.project:
        owner, proj_number = _parse_project_ref(config.project)
        muted(f"Checking project status in {owner}/{proj_number}.")
        project_status = _fetch_project_items(owner, proj_number)
        if project_status:
            muted(f"Found {len(project_status)} project items.")
    else:
        muted("No GitHub project configured — skipping project status checks.")

    merged: dict[int, Candidate] = {}
    for c in issue_candidates:
        merged[c.number] = c
    for num, status in project_status.items():
        if num in merged:
            merged[num].status = status

    filtered = [c for c in merged.values() if c.status.lower() not in _BLOCKED_STATUSES]
    claimed = _claimed_issue_numbers()
    filtered = [c for c in filtered if c.number not in claimed]

    if not filtered:
        return []

    return rank(filtered)


def run_triage() -> None:
    show_banner(TRIAGE_BANNER)

    config = _load_config()

    candidates = get_candidates(config)

    if not candidates:
        warning("I could not find a good next issue to queue.")
        raise typer.Exit(0)

    llm_agent = next((agent for agent in config.agents if agent in {"claude", "opencode"}), None)
    if llm_agent is not None:
        muted(f"Asking {describe_agent(llm_agent, config.models)} to choose the best next issue.")
    else:
        muted("No configured recommendation model available; built-in ranking will be used if needed.")
    chosen_number = _llm_pick(candidates, config.agents, config.models)

    if chosen_number is not None:
        chosen = next(c for c in candidates if c.number == chosen_number)
        source = "llm"
        success(f"{describe_agent(llm_agent, config.models) if llm_agent else 'The configured model'} chose issue #{chosen.number}.")
    else:
        warning("The configured recommendation model could not choose, so I picked the top issue using the built-in rules.")
        chosen = candidates[0]
        source = "rule-based"

    queue = {
        "number": chosen.number,
        "title": chosen.title,
        "body": chosen.body,
        "rationale": f"Selected by {source}",
        "source": source,
        "picked_at": datetime.now(timezone.utc).isoformat(),
    }
    qp = queue_path()
    qp.write_text(json.dumps(queue, indent=2) + "\n")

    console.print()
    console.print(
        warm_panel(
            f"[question]Picked #{chosen.number}:[/question] {chosen.title}\n\n"
            f"[muted]Source: {source} | Age: {chosen.age_days}d | Status: {chosen.status or 'none'}[/muted]",
            "Queue updated",
        )
    )
    console.print()
