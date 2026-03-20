from __future__ import annotations

import os
from typing import Any

import httpx

from kaneo.exceptions import AuthError, KaneoError, NotFoundError, ServerError, ValidationError


class KaneoClient:
    """HTTP client for the Kaneo API.

    Token and base URL can be supplied directly or via environment variables:
      KANEO_TOKEN    — API token (required if not passed explicitly)
      KANEO_BASE_URL — API base URL (optional, defaults to cloud.kaneo.app)
    """

    DEFAULT_BASE_URL = "https://cloud.kaneo.app/api"

    def __init__(
        self,
        token: str | None = None,
        base_url: str | None = None,
    ):
        resolved_token = token or os.environ.get("KANEO_TOKEN")
        if not resolved_token:
            raise ValueError(
                "token is required. Pass it explicitly or set the KANEO_TOKEN environment variable."
            )

        resolved_base_url = base_url or os.environ.get("KANEO_BASE_URL", self.DEFAULT_BASE_URL)
        self.base_url = resolved_base_url.rstrip("/")
        self._token = resolved_token
        self._http = httpx.Client(
            headers={
                "Authorization": f"Bearer {resolved_token}",
                "Content-Type": "application/json",
            },
            timeout=30,
        )

    # --- Resource accessors (lazy) ---

    @property
    def projects(self):
        from kaneo.resources.projects import ProjectsResource
        return ProjectsResource(self)

    @property
    def tasks(self):
        from kaneo.resources.tasks import TasksResource
        return TasksResource(self)

    @property
    def columns(self):
        from kaneo.resources.columns import ColumnsResource
        return ColumnsResource(self)

    @property
    def config(self):
        from kaneo.resources.config import ConfigResource
        return ConfigResource(self)

    # --- Internal HTTP helpers ---

    def _get(self, path: str, params: dict | None = None) -> Any:
        resp = self._http.get(self.base_url + path, params=params)
        return self._handle(resp)

    def _post(self, path: str, body: dict) -> Any:
        resp = self._http.post(self.base_url + path, json=body)
        return self._handle(resp)

    def _put(self, path: str, body: dict) -> Any:
        resp = self._http.put(self.base_url + path, json=body)
        return self._handle(resp)

    def _delete(self, path: str) -> Any:
        resp = self._http.delete(self.base_url + path)
        return self._handle(resp)

    def _handle(self, resp: httpx.Response) -> Any:
        if resp.status_code == 401:
            raise AuthError("Unauthorized — check your token", status_code=401)
        if resp.status_code == 404:
            raise NotFoundError("Resource not found", status_code=404)
        if resp.status_code == 400:
            msg = resp.json().get("message", "Bad request") if resp.content else "Bad request"
            raise ValidationError(msg, status_code=400)
        if resp.status_code >= 500:
            raise ServerError(f"Server error ({resp.status_code})", status_code=resp.status_code)
        if resp.status_code >= 400:
            raise KaneoError(f"HTTP {resp.status_code}", status_code=resp.status_code)
        if not resp.content:
            return {}
        return resp.json()
