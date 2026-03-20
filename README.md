# kaneo

[![CI](https://github.com/cloudpoet-com/kaneo-python-client/actions/workflows/ci.yml/badge.svg)](https://github.com/cloudpoet-com/kaneo-python-client/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/kaneo)](https://pypi.org/project/kaneo/)
[![Python](https://img.shields.io/pypi/pyversions/kaneo)](https://pypi.org/project/kaneo/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Python client and MCP server for the [Kaneo](https://kaneo.app) project management API.

**Two interfaces, one package:**

- **Python SDK** — use `kaneo` as a library in your Python code
- **MCP Server** — plug into Claude Code, Cursor, Windsurf, or any MCP-compatible AI tool

## Table of Contents

- [Installation](#installation)
- [Python SDK](#python-sdk)
  - [Quick Start](#quick-start)
  - [Environment Variables](#environment-variables)
  - [Self-hosted Kaneo](#self-hosted-kaneo)
  - [Projects](#projects)
  - [Tasks](#tasks)
  - [Columns](#columns)
  - [Config](#config)
  - [Error Handling](#error-handling)
- [MCP Server](#mcp-server-for-ai-agents)
  - [Setup for Claude Code](#claude-code)
  - [Setup for Cursor](#cursor)
  - [Available Tools](#available-tools)
- [Development](#development)
- [License](#license)

## Installation

```bash
# SDK only
pip install kaneo

# SDK + MCP server
pip install kaneo[mcp]
```

Requires Python 3.10+.

---

## Python SDK

### Quick Start

```python
from kaneo import KaneoClient

# Reads KANEO_TOKEN from environment automatically
client = KaneoClient()

# Or pass credentials explicitly
client = KaneoClient(token="your-api-token")

# List projects
projects = client.projects.list(workspace_id="your-workspace-id")
for p in projects:
    print(f"{p.name} ({p.slug})")

# Create a task
task = client.tasks.create(
    project_id="your-project-id",
    title="Fix the login bug",
    priority="high",
    status="to-do",
    description="Users are getting 500 errors on /login",
)
print(f"Created: {task.id}")

# Update task status
updated = client.tasks.update_status(task.id, "in-progress")
print(f"Status: {updated.status}")
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `KANEO_TOKEN` | Yes (if not passed explicitly) | — | Your Kaneo API token |
| `KANEO_BASE_URL` | No | `https://cloud.kaneo.app/api` | API base URL |

Both can be overridden by passing `token` and `base_url` to `KaneoClient()`.

### Self-hosted Kaneo

```bash
export KANEO_TOKEN=your-token
export KANEO_BASE_URL=https://kaneo.yourdomain.com/api
```

```python
# Or explicitly
client = KaneoClient(
    token="your-token",
    base_url="https://kaneo.yourdomain.com/api",
)
```

### Projects

```python
# List all projects in a workspace
projects = client.projects.list(workspace_id="ws-id")

# Get a single project (includes nested tasks)
project = client.projects.get(project_id="proj-id", workspace_id="ws-id")
print(project.name, project.is_public, len(project.tasks))

# Create a project
project = client.projects.create(
    workspace_id="ws-id",
    name="My Project",
    slug="MP",
    icon="Layout",
)

# Delete a project
client.projects.delete(project_id="proj-id")
```

### Tasks

```python
# List all tasks in a project (flattened from all board columns)
tasks = client.tasks.list(project_id="proj-id")

# Get a single task
task = client.tasks.get(task_id="task-id")

# Create a task
task = client.tasks.create(
    project_id="proj-id",
    title="Implement OAuth",
    priority="high",        # no-priority | low | medium | high | urgent
    status="to-do",         # backlog | to-do | in-progress | done | cancelled
    description="Add Google OAuth support",
    due_date="2026-12-31",  # optional
    user_id="user-id",      # optional — assignee
)

# Update individual fields
client.tasks.update_status(task.id, "in-progress")
client.tasks.update_priority(task.id, "urgent")
client.tasks.update_title(task.id, "Implement OAuth 2.0")
client.tasks.update_description(task.id, "Add Google and GitHub OAuth")

# Delete a task
client.tasks.delete(task_id="task-id")
```

**Valid priorities:** `no-priority`, `low`, `medium`, `high`, `urgent`

**Valid statuses:** `backlog`, `to-do`, `in-progress`, `done`, `cancelled`

Invalid values raise `ValueError` before any API call is made.

### Columns

```python
# Create a board column
client.columns.create(
    project_id="proj-id",
    name="In Review",
    is_final=False,  # set True for "done"-type columns
)

# Delete a column
client.columns.delete(column_id="col-id")
```

### Config

```python
# Get server configuration
config = client.config.get()
print(config.has_smtp)
print(config.has_github_sign_in)
print(config.disable_registration)
```

### Error Handling

All errors inherit from `KaneoError` and include a `status_code` attribute:

```python
from kaneo.exceptions import AuthError, NotFoundError, ValidationError, ServerError

try:
    task = client.tasks.get("nonexistent-id")
except NotFoundError as e:
    print(f"Not found (HTTP {e.status_code})")
except AuthError:
    print("Check your KANEO_TOKEN")
except ValidationError as e:
    print(f"Bad request: {e}")
except ServerError:
    print("Kaneo server error — try again later")
```

| Exception | HTTP Status | When |
|-----------|-------------|------|
| `AuthError` | 401 | Invalid or missing token |
| `NotFoundError` | 404 | Resource doesn't exist |
| `ValidationError` | 400 | Bad input / missing fields |
| `ServerError` | 5xx | Server-side failure |
| `KaneoError` | Any 4xx | Base class / catch-all |

---

## MCP Server (for AI agents)

The MCP server exposes all SDK operations as tools that AI agents can call over the [Model Context Protocol](https://modelcontextprotocol.io). Any MCP-compatible tool can use it.

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

For self-hosted Kaneo, add `KANEO_BASE_URL`:

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

| Tool | Description |
|------|-------------|
| `get_config` | Get Kaneo server configuration |
| `list_projects` | List all projects in workspace |
| `get_project` | Get project by ID with tasks |
| `create_project` | Create a new project |
| `delete_project` | Delete a project |
| `list_tasks` | List all tasks in a project |
| `get_task` | Get a single task by ID |
| `create_task` | Create a task (title, priority, status, description, due date, assignee) |
| `delete_task` | Delete a task |
| `update_task_status` | Change status: backlog / to-do / in-progress / done / cancelled |
| `update_task_priority` | Change priority: no-priority / low / medium / high / urgent |
| `update_task_title` | Update task title |
| `update_task_description` | Update task description (supports markdown) |
| `create_column` | Create a board column |
| `delete_column` | Delete a board column |

### MCP Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `KANEO_TOKEN` | Yes | — | API token |
| `KANEO_BASE_URL` | No | `https://cloud.kaneo.app/api` | API base URL (for self-hosted) |
| `KANEO_WORKSPACE_ID` | No | — | Default workspace ID (avoids passing it to every project tool) |

---

## Development

```bash
# Clone and install
git clone https://github.com/cloudpoet-com/kaneo-python-client.git
cd kaneo-python-client
pip install -e ".[dev,mcp]"

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=src/kaneo --cov-report=term-missing

# Lint
black --check src/ tests/
isort --check-only src/ tests/
flake8 src/ tests/ --max-line-length=88

# Build
pip install build
python -m build
```

### Project Structure

```
src/kaneo/
  __init__.py           # exports KaneoClient + models
  client.py             # HTTP client with auth, error handling
  exceptions.py         # KaneoError, AuthError, NotFoundError, etc.
  models/
    project.py          # Project dataclass
    task.py             # Task dataclass
    config.py           # Config dataclass
  resources/
    projects.py         # ProjectsResource (list, get, create, delete)
    tasks.py            # TasksResource (CRUD + field-level updates)
    columns.py          # ColumnsResource (create, delete)
    config.py           # ConfigResource (get)
  mcp/
    server.py           # MCP server — wraps SDK as tools
tests/
  test_client.py        # HTTP client + error handling tests
  test_models.py        # Dataclass mapping tests
  test_projects.py      # ProjectsResource tests
  test_tasks.py         # TasksResource tests
  test_columns.py       # ColumnsResource tests
  test_config.py        # ConfigResource tests
  test_mcp_server.py    # MCP tool function tests
```

## License

MIT
