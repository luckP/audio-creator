"""Shared fixtures for unit tests."""

import tempfile
import shutil
from pathlib import Path
import pytest

from app.utils.config import Config, DatabaseConfig


@pytest.fixture
def temp_db_path():
    """Create a temporary directory for test database."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir) / "test.db"
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def test_config(temp_db_path, monkeypatch):
    """Mock configuration to use temporary database."""
    test_config = Config(
        database=DatabaseConfig(path=str(temp_db_path), echo=False)
    )
    
    # Mock get_config to return our test config
    monkeypatch.setattr("app.models.database.get_config", lambda: test_config)
    
    # Reset global engine and session factory
    import app.models.database as db_module
    db_module._engine = None
    db_module._SessionLocal = None
    
    yield test_config
    
    # Cleanup
    db_module._engine = None
    db_module._SessionLocal = None
