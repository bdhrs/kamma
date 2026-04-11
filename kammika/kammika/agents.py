from dataclasses import dataclass
import subprocess


CLAUDE_MODEL = "opus"
OPENCODE_MODEL = "openai/gpt-5.4"


@dataclass(frozen=True)
class AgentSpec:
    key: str
    label: str
    executable: str
    probe_args: tuple[str, ...] = ("--help",)


SUPPORTED_AGENTS: tuple[AgentSpec, ...] = (
    AgentSpec("claude", "Claude Code", "claude"),
    AgentSpec("gemini", "Gemini CLI", "gemini"),
    AgentSpec("opencode", "OpenCode", "opencode"),
    AgentSpec("codex", "Codex CLI", "codex"),
    AgentSpec("kilo", "Kilo CLI", "kilo"),
    AgentSpec("qwen", "Qwen Code", "qwen"),
)

SUPPORTED_AGENT_MAP = {spec.key: spec for spec in SUPPORTED_AGENTS}
DEFAULT_AGENT_ORDER = [spec.key for spec in SUPPORTED_AGENTS]


def supported_agent_specs() -> tuple[AgentSpec, ...]:
    return SUPPORTED_AGENTS


def get_agent_spec(agent: str) -> AgentSpec | None:
    return SUPPORTED_AGENT_MAP.get(agent)


def get_agent_model(agent: str, models: dict[str, str] | None = None) -> str | None:
    model_overrides = models or {}
    if agent == "claude":
        return model_overrides.get("claude", CLAUDE_MODEL)
    if agent == "opencode":
        return model_overrides.get("opencode", OPENCODE_MODEL)
    if agent in {"gemini", "codex", "kilo", "qwen"}:
        return model_overrides.get(agent)
    return None


def describe_agent(agent: str, models: dict[str, str] | None = None) -> str:
    spec = get_agent_spec(agent)
    label = spec.label if spec else agent
    model = get_agent_model(agent, models)
    if model:
        return f"{label} ({model})"
    return label


def supported_agent_keys(agents: list[str]) -> list[str]:
    return [agent for agent in agents if agent in SUPPORTED_AGENT_MAP]


def detect_available_agents(
    run_command,
) -> list[str]:
    detected: list[str] = []
    for spec in SUPPORTED_AGENTS:
        try:
            result = run_command([spec.executable, *spec.probe_args])
        except FileNotFoundError:
            continue
        if result.returncode == 0:
            detected.append(spec.key)
    return detected


def build_launch_command(
    agent: str,
    initial_instruction: str,
    models: dict[str, str] | None = None,
) -> list[str]:
    model_overrides = models or {}

    if agent == "claude":
        return [
            "claude",
            "--model",
            model_overrides.get("claude", CLAUDE_MODEL),
            "--dangerously-skip-permissions",
            initial_instruction,
        ]
    if agent == "gemini":
        cmd = ["gemini"]
        model = model_overrides.get("gemini")
        if model:
            cmd.extend(["--model", model])
        cmd.extend(["--prompt-interactive", initial_instruction])
        return cmd
    if agent == "opencode":
        return [
            "opencode",
            "--model",
            model_overrides.get("opencode", OPENCODE_MODEL),
            "--prompt",
            initial_instruction,
        ]
    if agent == "codex":
        cmd = ["codex"]
        model = model_overrides.get("codex")
        if model:
            cmd.extend(["--model", model])
        cmd.append(initial_instruction)
        return cmd
    if agent == "kilo":
        cmd = ["kilo"]
        model = model_overrides.get("kilo")
        if model:
            cmd.extend(["--model", model])
        cmd.extend(["--prompt", initial_instruction])
        return cmd
    if agent == "qwen":
        cmd = ["qwen"]
        model = model_overrides.get("qwen")
        if model:
            cmd.extend(["--model", model])
        cmd.extend(["--prompt-interactive", initial_instruction])
        return cmd
    raise ValueError(f"Unknown agent '{agent}'")


def subprocess_probe(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True)
