from dataclasses import dataclass, field
from typing import Any


@dataclass
class KammikaConfig:
    repo: str
    project: str
    agents: list[str] = field(default_factory=lambda: ["claude", "opencode"])
    models: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "repo": self.repo,
            "project": self.project,
            "agents": self.agents,
            "models": self.models,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KammikaConfig":
        return cls(
            repo=data["repo"],
            project=data["project"],
            agents=data.get("agents", ["claude", "opencode"]),
            models=data.get("models", {}),
        )
