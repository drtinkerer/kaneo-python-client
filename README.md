# kaneo

[![CI](https://github.com/drtinkerer/kaneo-python-client/actions/workflows/ci.yml/badge.svg)](https://github.com/drtinkerer/kaneo-python-client/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/kaneo)](https://pypi.org/project/kaneo/)
[![Python](https://img.shields.io/pypi/pyversions/kaneo)](https://pypi.org/project/kaneo/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A Python SDK and MCP server for the [Kaneo](https://kaneo.app) project management API.

Use it as a **Python library** in your scripts, or as an **MCP server** that plugs straight into Claude Code, Cursor, Windsurf, or any MCP-compatible AI tool.

## Installation

```bash
pip install kaneo          # just the SDK
pip install kaneo[mcp]     # SDK + MCP server for AI agents
```

Requires Python 3.10+.

---

## Python SDK

### Quick Start

```python
from kaneo import KaneoClient

# picks up KANEO_TOKEN from your environment
client = KaneoClient()

# or pass it directly
client = KaneoClient(token="your-api-token")

# list every project in a workspace
projects = client.projects.list(workspace_id="your-workspace-id")
for p in projects:
    print(f"{p.name} ({p.slug})")

# create a task
task = client.tasks.create(
    project_id="your-project-id",
    title="Fix the login bug",
    priority="high",
    status="to-do",
    description="Users are seeing 500 errors on /login",
)
print(f"Created: {task.id}")

# move it to in-progress
updated = client.tasks.update_status(task.id, "in-progress")
print(f"Status: {updated.status}")
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `KANEO_TOKEN` | Yes (unless passed to constructor) | — | Your Kaneo API token |
| `KANEO_BASE_URL` | No | `https://cloud.kaneo.app/api` | API base URL |

You can always override these by passing `token` and `base_url` to `KaneoClient()`.

### Self-hosted Kaneo

If you're running your own Kaneo instance, just point the client at it:

```bash
export KANEO_TOKEN=your-token
export KANEO_BASE_URL=https://kaneo.yourdomain.com/api
```

```python
# or in code
client = KaneoClient(
    token="your-token",
    base_url="https://kaneo.yourdomain.com/api",
)
```

### Projects

```python
# list all projects in a workspace
projects = client.projects.list(workspace_id="ws-id")

# get a single project (comes with its tasks)
project = client.projects.get(project_id="proj-id", workspace_id="ws-id")
print(project.name, project.is_public, len(project.tasks))

# create one
project = client.projects.create(
    workspace_id="ws-id",
    name="My Project",
    slug="MP",
    icon="Layout",
)

# delete it
client.projects.delete(project_id="proj-id")
```

### Tasks

```python
# list all tasks in a project (pulled from every board column)
tasks = client.tasks.list(project_id="proj-id")

# get a single task
task = client.tasks.get(task_id="task-id")

# create a task with all the options
task = client.tasks.create(
    project_id="proj-id",
    title="Implement OAuth",
    priority="high",        # no-priority | low | medium | high | urgent
    status="to-do",         # backlog | to-do | in-progress | done | cancelled
    description="Add Google OAuth support",
    due_date="2026-12-31",  # optional
    user_id="user-id",      # optional assignee
)

# update fields individually
client.tasks.update_status(task.id, "in-progress")
client.tasks.update_priority(task.id, "urgent")
client.tasks.update_title(task.id, "Implement OAuth 2.0")
client.tasks.update_description(task.id, "Add Google and GitHub OAuth")

# delete
client.tasks.delete(task_id="task-id")
```

**Priorities:** `no-priority`, `low`, `medium`, `high`, `urgent`

**Statuses:** `backlog`, `to-do`, `in-progress`, `done`, `cancelled`

Pass something invalid and you'll get a `ValueError` before the API is even called.

### Columns

```python
# add a column to a project board
client.columns.create(
    project_id="proj-id",
    name="In Review",
    is_final=False,  # True for columns that mean "done"
)

# remove a column
client.columns.delete(column_id="col-id")
```

### Config

```python
# check what the server has enabled
config = client.config.get()
print(config.has_smtp)
print(config.has_github_sign_in)
print(config.disable_registration)
```

### Error Handling

Every exception carries a `status_code` so you know exactly what went wrong:

```python
from kaneo.exceptions import AuthError, NotFoundError, ValidationError, ServerError

try:
    task = client.tasks.get("nonexistent-id")
except NotFoundError as e:
    print(f"Not found (HTTP {e.status_code})")
except AuthError:
    print("Bad token — check KANEO_TOKEN")
except ValidationError as e:
    print(f"Bad request: {e}")
except ServerError:
    print("Kaneo is having a bad day — try again later")
```

| Exception | HTTP Status | When |
|-----------|-------------|------|
| `AuthError` | 401 | Invalid or missing token |
| `NotFoundError` | 404 | Resource doesn't exist |
| `ValidationError` | 400 | Bad input or missing fields |
| `ServerError` | 5xx | Server-side failure |
| `KaneoError` | Any other 4xx | Catch-all base class |

---

## MCP Server (for AI agents)

The MCP server wraps the SDK and exposes every operation as a tool over the [Model Context Protocol](https://modelcontextprotocol.io). Your AI agent discovers the tools automatically — no extra prompting needed.

```
your AI tool  <--stdin/stdout-->  kaneo-mcp  <--HTTPS-->  Kaneo API
```

### Install

```bash
pip install kaneo[mcp]
```

### Claude Code

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "kaneo": {
      "command": "kaneo-mcp",
      "env": {
        "KANEO_TOKEN": "your-api-token",
        "KANEO_WORKSPACE_ID": "your-workspace-id"
      }
    }
  }
}
```

Self-hosted? Just add `KANEO_BASE_URL`:

```json
{
  "mcpServers": {
    "kaneo": {
      "command": "kaneo-mcp",
      "env": {
        "KANEO_TOKEN": "your-api-token",
        "KANEO_WORKSPACE_ID": "your-workspace-id",
        "KANEO_BASE_URL": "https://kaneo.yourdomain.com/api"
      }
    }
  }
}
```

### Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "kaneo": {
      "command": "kaneo-mcp",
      "env": {
        "KANEO_TOKEN": "your-api-token",
        "KANEO_WORKSPACE_ID": "your-workspace-id"
      }
    }
  }
}
```

### Available Tools

| Tool | What it does |
|------|-------------|
| `get_config` | Check server settings (SMTP, SSO, registration) |
| `list_projects` | List all projects in a workspace |
| `get_project` | Get a project with its tasks |
| `create_project` | Create a new project |
| `delete_project` | Delete a project |
| `list_tasks` | List all tasks in a project |
| `get_task` | Get a single task by ID |
| `create_task` | Create a task with title, priority, status, description, due date, assignee |
| `delete_task` | Delete a task |
| `update_task_status` | Move a task: backlog / to-do / in-progress / done / cancelled |
| `update_task_priority` | Reprioritize: no-priority / low / medium / high / urgent |
| `update_task_title` | Rename a task |
| `update_task_description` | Edit task description (markdown supported) |
| `create_column` | Add a board column |
| `delete_column` | Remove a board column |

### MCP Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `KANEO_TOKEN` | Yes | — | API token |
| `KANEO_BASE_URL` | No | `https://cloud.kaneo.app/api` | For self-hosted instances |
| `KANEO_WORKSPACE_ID` | No | — | Default workspace (saves passing it to every project tool) |

---

## Development

```bash
git clone https://github.com/drtinkerer/kaneo-python-client.git
cd kaneo-python-client
pip install -e ".[dev,mcp]"

# run tests
pytest tests/ -v

# with coverage
pytest tests/ --cov=src/kaneo --cov-report=term-missing

# lint
black --check src/ tests/
isort --check-only src/ tests/
flake8 src/ tests/ --max-line-length=88

# build
pip install build && python -m build
```

### Project Layout

```
src/kaneo/
  client.py             HTTP client, auth, error handling
  exceptions.py         typed exceptions (AuthError, NotFoundError, etc.)
  models/
    project.py          Project dataclass
    task.py             Task dataclass
    config.py           Config dataclass
  resources/
    projects.py         list, get, create, delete
    tasks.py            CRUD + field-level updates
    columns.py          create, delete
    config.py           get
  mcp/
    server.py           MCP server wrapping the SDK
```

## License

MIT
