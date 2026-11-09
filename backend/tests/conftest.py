import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


@pytest.fixture
def settings(tmp_path) -> Settings:
    # Real assets, isolated storage, and no API key from the developer's .env.
    return Settings(_env_file=None, storage_dir=tmp_path / "storage", groq_api_key=None)


@pytest.fixture
def client(settings) -> TestClient:
    with TestClient(create_app(settings)) as test_client:
        yield test_client
