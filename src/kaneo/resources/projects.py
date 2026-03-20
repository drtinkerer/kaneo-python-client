from __future__ import annotations

from kaneo.models.project import Project


class ProjectsResource:
    def __init__(self, client):
        self._client = client

    def list(self, workspace_id: str) -> list[Project]:
        """List all projects in a workspace."""
        data = self._client._get("/project", params={"workspaceId": workspace_id})
        return [Project.from_dict(p) for p in data]

    def get(self, project_id: str, workspace_id: str) -> Project:
        """Get a specific project by ID."""
        data = self._client._get(f"/project/{project_id}", params={"workspaceId": workspace_id})
        return Project.from_dict(data)

    def create(self, workspace_id: str, name: str, slug: str, icon: str = "Layout") -> Project:
        """Create a new project in a workspace."""
        data = self._client._post("/project", {
            "workspaceId": workspace_id,
            "name": name,
            "slug": slug,
            "icon": icon,
        })
        return Project.from_dict(data)

    def delete(self, project_id: str) -> Project:
        """Delete a project by ID."""
        data = self._client._delete(f"/project/{project_id}")
        if isinstance(data, list):
            data = data[0]
        return Project.from_dict(data)
