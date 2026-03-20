import pytest
from kaneo import KaneoClient

BASE_URL = "https://cloud.kaneo.app/api"
TOKEN = "test-token"


@pytest.fixture
def client():
    return KaneoClient(base_url=BASE_URL, token=TOKEN)
