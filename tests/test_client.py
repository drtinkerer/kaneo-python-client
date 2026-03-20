import pytest
from pytest_httpx import HTTPXMock
from kaneo import KaneoClient
from kaneo.exceptions import AuthError, NotFoundError, ServerError, ValidationError


def test_client_sets_auth_header(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url="https://cloud.kaneo.app/api/config", json={})
    client._get("/config")
    request = httpx_mock.get_requests()[0]
    assert request.headers["Authorization"] == "Bearer test-token"


def test_client_sets_content_type_on_post(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url="https://cloud.kaneo.app/api/project", json={})
    client._post("/project", {"name": "x"})
    request = httpx_mock.get_requests()[0]
    assert request.headers["Content-Type"] == "application/json"


def test_client_raises_auth_error_on_401(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url="https://cloud.kaneo.app/api/config", status_code=401)
    with pytest.raises(AuthError) as exc:
        client._get("/config")
    assert exc.value.status_code == 401


def test_client_raises_not_found_on_404(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url="https://cloud.kaneo.app/api/config", status_code=404)
    with pytest.raises(NotFoundError) as exc:
        client._get("/config")
    assert exc.value.status_code == 404


def test_client_raises_validation_error_on_400(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://cloud.kaneo.app/api/config", status_code=400, json={"message": "bad input"}
    )
    with pytest.raises(ValidationError) as exc:
        client._get("/config")
    assert "bad input" in str(exc.value)


def test_client_raises_server_error_on_500(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url="https://cloud.kaneo.app/api/config", status_code=500)
    with pytest.raises(ServerError):
        client._get("/config")


def test_client_custom_base_url():
    c = KaneoClient(base_url="https://self-hosted.example.com/api", token="tok")
    assert c.base_url == "https://self-hosted.example.com/api"


def test_client_reads_token_from_env(monkeypatch):
    monkeypatch.setenv("KANEO_TOKEN", "env-token")
    monkeypatch.delenv("KANEO_BASE_URL", raising=False)
    c = KaneoClient()
    assert c._token == "env-token"
    assert c.base_url == KaneoClient.DEFAULT_BASE_URL


def test_client_reads_base_url_from_env(monkeypatch):
    monkeypatch.setenv("KANEO_TOKEN", "env-token")
    monkeypatch.setenv("KANEO_BASE_URL", "https://self-hosted.example.com/api")
    c = KaneoClient()
    assert c.base_url == "https://self-hosted.example.com/api"


def test_client_raises_without_token(monkeypatch):
    monkeypatch.delenv("KANEO_TOKEN", raising=False)
    with pytest.raises(ValueError, match="KANEO_TOKEN"):
        KaneoClient()
