from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Task:
    id: str
    project_id: str
    title: str
    status: str
    priority: str
    position: int
    number: int
    description: str = ""
    column_id: str | None = None
    user_id: str | None = None
    due_date: str | None = None
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        return cls(
            id=data["id"],
            project_id=data["projectId"],
            title=data["title"],
            status=data["status"],
            priority=data["priority"],
            position=data.get("position", 0),
            number=data.get("number", 0),
            description=data.get("description") or "",
            column_id=data.get("columnId"),
            user_id=data.get("userId"),
            due_date=data.get("dueDate"),
            created_at=data.get("createdAt", ""),
        )
