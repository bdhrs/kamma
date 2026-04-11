import subprocess
from pathlib import Path


def target_repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError("Not inside a git repository.")
    return Path(result.stdout.strip())


def kamma_dir() -> Path:
    return target_repo_root() / "kamma"


def config_path() -> Path:
    return kamma_dir() / "kammika.config.json"


def queue_path() -> Path:
    return kamma_dir() / "kammika.queue.json"
