from kaneo.models.config import Config
from kaneo.models.project import Project
from kaneo.models.task import Task


def test_task_from_dict_maps_camel_to_snake():
    data = {
        "id": "t1", "projectId": "p1", "title": "Do it",
        "status": "to-do", "priority": "high", "position": 2,
        "number": 3, "description": "desc", "columnId": "c1",
        "userId": "u1", "dueDate": "2026-12-31", "createdAt": "2026-01-01T00:00:00Z",
    }
    task = Task.from_dict(data)
    assert task.id == "t1"
    assert task.project_id == "p1"
    assert task.column_id == "c1"
    assert task.user_id == "u1"
    assert task.due_date == "2026-12-31"


def test_task_from_dict_handles_missing_optional_fields():
    data = {
        "id": "t1", "projectId": "p1", "title": "Do it",
        "status": "to-do", "priority": "low", "position": 0, "number": 1,
    }
    task = Task.from_dict(data)
    assert task.column_id is None
    assert task.description == ""
    assert task.due_date is None


def test_project_from_dict_includes_nested_tasks():
    data = {
        "id": "p1", "workspaceId": "ws1", "name": "Proj", "slug": "P",
        "icon": "Layout", "isPublic": True, "createdAt": "2026-01-01T00:00:00Z",
        "tasks": [
            {"id": "t1", "projectId": "p1", "title": "T", "status": "to-do",
             "priority": "low", "position": 0, "number": 1}
        ],
    }
    project = Project.from_dict(data)
    assert project.workspace_id == "ws1"
    assert project.is_public is True
    assert len(project.tasks) == 1
    assert isinstance(project.tasks[0], Task)


def test_config_from_dict_maps_all_flags():
    data = {
        "disableRegistration": True, "isDemoMode": False, "hasSmtp": True,
        "hasGithubSignIn": True, "hasGoogleSignIn": False,
        "hasDiscordSignIn": False, "hasCustomOAuth": False, "hasGuestAccess": True,
    }
    cfg = Config.from_dict(data)
    assert cfg.disable_registration is True
    assert cfg.has_smtp is True
    assert cfg.has_google_sign_in is False
