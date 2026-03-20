from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from kaneo.models.task import Task


@dataclass
class Project:
    id: str
    workspace_id: str
    name: str
    slug: str
    icon: str
    is_public: bool = False
    description: str | None = None
    created_at: str = ""
    tasks: list[Task] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Project:
        return cls(
            id=data["id"],
            workspace_id=data["workspaceId"],
            name=data["name"],
            slug=data["slug"],
            icon=data.get("icon", ""),
            is_public=data.get("isPublic", False),
            description=data.get("description"),
            created_at=data.get("createdAt", ""),
            tasks=[Task.from_dict(t) for t in data.get("tasks", [])],
        )
