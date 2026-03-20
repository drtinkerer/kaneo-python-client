from __future__ import annotations

from kaneo.models.task import Task

VALID_PRIORITIES = {"no-priority", "low", "medium", "high", "urgent"}
VALID_STATUSES = {"backlog", "to-do", "in-progress", "done", "cancelled"}


class TasksResource:
    def __init__(self, client):
        self._client = client

    def list(self, project_id: str) -> list[Task]:
        """List all tasks in a project.

        The API returns tasks grouped by columns. This method
        flattens them into a single list.
        """
        data = self._client._get(f"/task/tasks/{project_id}")
        tasks = []
        for column in data.get("columns", []):
            for t in column.get("tasks", []):
                tasks.append(Task.from_dict(t))
        return tasks

    def get(self, task_id: str) -> Task:
        """Get a task by ID."""
        data = self._client._get(f"/task/{task_id}")
        return Task.from_dict(data)

    def create(
        self,
        project_id: str,
        title: str,
        priority: str = "no-priority",
        status: str = "to-do",
        description: str = "",
        due_date: str | None = None,
        user_id: str | None = None,
    ) -> Task:
        """Create a new task in a project."""
        if priority not in VALID_PRIORITIES:
            raise ValueError(f"Invalid priority '{priority}'. Must be one of: {VALID_PRIORITIES}")
        body: dict = {
            "title": title,
            "description": description,
            "priority": priority,
            "status": status,
        }
        if due_date:
            body["dueDate"] = due_date
        if user_id:
            body["userId"] = user_id
        data = self._client._post(f"/task/{project_id}", body)
        return Task.from_dict(data)

    def delete(self, task_id: str) -> Task:
        """Delete a task by ID."""
        data = self._client._delete(f"/task/{task_id}")
        if isinstance(data, list):
            data = data[0]
        return Task.from_dict(data)

    def update_status(self, task_id: str, status: str) -> Task:
        """Update the status of a task."""
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status '{status}'. Must be one of: {VALID_STATUSES}")
        self._client._put(f"/task/status/{task_id}", {"status": status})
        return self.get(task_id)

    def update_priority(self, task_id: str, priority: str) -> Task:
        """Update the priority of a task."""
        if priority not in VALID_PRIORITIES:
            raise ValueError(f"Invalid priority '{priority}'. Must be one of: {VALID_PRIORITIES}")
        self._client._put(f"/task/priority/{task_id}", {"priority": priority})
        return self.get(task_id)

    def update_title(self, task_id: str, title: str) -> Task:
        """Update the title of a task."""
        self._client._put(f"/task/title/{task_id}", {"title": title})
        return self.get(task_id)

    def update_description(self, task_id: str, description: str) -> Task:
        """Update the description of a task."""
        self._client._put(f"/task/description/{task_id}", {"description": description})
        return self.get(task_id)
