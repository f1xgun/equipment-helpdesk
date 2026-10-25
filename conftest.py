import pytest

from app import config


@pytest.fixture
def isolated_database(monkeypatch, tmp_path):
    database_path = tmp_path / "test.db"
    monkeypatch.setattr(config, "ENV_FILE", tmp_path / ".env")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path}")
    return database_path
