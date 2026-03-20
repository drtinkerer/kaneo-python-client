import pytest
from pytest_httpx import HTTPXMock
from kaneo.models import Task

PROJECT_ID = "proj-abc"

TASK_DATA = {
    "id": "task-xyz",
    "projectId": PROJECT_ID,
    "title": "Fix the bug",
    "description": "Details here",
    "status": "to-do",
    "priority": "high",
    "position": 1,
    "number": 1,
    "columnId": None,
    "userId": None,
    "dueDate": None,
    "createdAt": "2026-01-01T00:00:00.000Z",
}


def test_list_tasks(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url=f"https://cloud.kaneo.app/api/task/tasks/{PROJECT_ID}",
        json={
            "columns": [
                {"id": "to-do", "name": "To Do", "tasks": [TASK_DATA]},
                {"id": "done", "name": "Done", "tasks": []},
            ]
        },
    )
    tasks = client.tasks.list(PROJECT_ID)
    assert len(tasks) == 1
    assert isinstance(tasks[0], Task)
    assert tasks[0].title == "Fix the bug"


def test_get_task(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url="https://cloud.kaneo.app/api/task/task-xyz", json=TASK_DATA)
    task = client.tasks.get("task-xyz")
    assert isinstance(task, Task)
    assert task.title == "Fix the bug"
    assert task.priority == "high"


def test_create_task(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url=f"https://cloud.kaneo.app/api/task/{PROJECT_ID}", json=TASK_DATA
    )
    task = client.tasks.create(
        project_id=PROJECT_ID,
        title="Fix the bug",
        priority="high",
        status="to-do",
    )
    assert isinstance(task, Task)
    assert task.id == "task-xyz"


def test_delete_task(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url="https://cloud.kaneo.app/api/task/task-xyz", json=TASK_DATA)
    deleted = client.tasks.delete("task-xyz")
    assert deleted.id == "task-xyz"


def test_update_status(client, httpx_mock: HTTPXMock):
    updated = {**TASK_DATA, "status": "in-progress"}
    httpx_mock.add_response(url="https://cloud.kaneo.app/api/task/status/task-xyz", json=TASK_DATA)
    httpx_mock.add_response(url="https://cloud.kaneo.app/api/task/task-xyz", json=updated)
    task = client.tasks.update_status("task-xyz", "in-progress")
    assert task.status == "in-progress"


def test_update_priority(client, httpx_mock: HTTPXMock):
    updated = {**TASK_DATA, "priority": "urgent"}
    httpx_mock.add_response(url="https://cloud.kaneo.app/api/task/priority/task-xyz", json=TASK_DATA)
    httpx_mock.add_response(url="https://cloud.kaneo.app/api/task/task-xyz", json=updated)
    task = client.tasks.update_priority("task-xyz", "urgent")
    assert task.priority == "urgent"


def test_update_title(client, httpx_mock: HTTPXMock):
    updated = {**TASK_DATA, "title": "New title"}
    httpx_mock.add_response(url="https://cloud.kaneo.app/api/task/title/task-xyz", json=TASK_DATA)
    httpx_mock.add_response(url="https://cloud.kaneo.app/api/task/task-xyz", json=updated)
    task = client.tasks.update_title("task-xyz", "New title")
    assert task.title == "New title"


def test_update_description(client, httpx_mock: HTTPXMock):
    updated = {**TASK_DATA, "description": "New desc"}
    httpx_mock.add_response(url="https://cloud.kaneo.app/api/task/description/task-xyz", json=TASK_DATA)
    httpx_mock.add_response(url="https://cloud.kaneo.app/api/task/task-xyz", json=updated)
    task = client.tasks.update_description("task-xyz", "New desc")
    assert task.description == "New desc"


def test_invalid_priority_raises(client):
    with pytest.raises(ValueError, match="Invalid priority"):
        client.tasks.create(project_id=PROJECT_ID, title="x", priority="super-urgent", status="to-do")


def test_invalid_status_raises(client):
    with pytest.raises(ValueError, match="Invalid status"):
        client.tasks.update_status("task-xyz", "limbo")
