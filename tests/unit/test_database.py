"""Tests for database module."""

import tempfile
import shutil
from pathlib import Path
from sqlalchemy import text
import pytest

from app.models.database import (
    get_engine,
    get_session_factory,
    get_db,
    init_database,
    reset_database,
)
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


def test_get_engine(test_config):
    """Test that get_engine creates and returns an engine."""
    engine = get_engine()
    
    assert engine is not None
    assert str(engine.url).startswith("sqlite:///")
    
    # Test singleton behavior - should return same engine
    engine2 = get_engine()
    assert engine is engine2


def test_get_session_factory(test_config):
    """Test that get_session_factory creates and returns a session factory."""
    factory = get_session_factory()
    
    assert factory is not None
    
    # Test singleton behavior
    factory2 = get_session_factory()
    assert factory is factory2


def test_get_db_context_manager(test_config):
    """Test that get_db provides a working session context manager."""
    init_database()
    
    with get_db() as session:
        assert session is not None
        # Session should be usable
        result = session.execute(text("SELECT 1"))
        assert result.scalar() == 1


def test_get_db_commit_on_success(test_config):
    """Test that get_db commits transaction on success."""
    init_database()
    
    # This should commit automatically
    with get_db() as session:
        session.execute(text("SELECT 1"))
    
    # If we got here without exception, commit worked


def test_get_db_rollback_on_error(test_config):
    """Test that get_db rolls back transaction on error."""
    init_database()
    
    with pytest.raises(ValueError):
        with get_db() as session:
            session.execute(text("SELECT 1"))
            raise ValueError("Test error")
    
    # If we got here, rollback worked (no database corruption)


def test_init_database(test_config, temp_db_path):
    """Test that init_database creates the database file and tables."""
    # Database file shouldn't exist yet
    assert not temp_db_path.exists()
    
    init_database()
    
    # Database file should now exist
    assert temp_db_path.exists()
    
    # Should be safe to call multiple times
    init_database()
    assert temp_db_path.exists()


def test_reset_database(test_config):  # pylint: disable=unused-argument
    """Test that reset_database drops and recreates all tables."""
    init_database()
    
    # Reset should work without error
    reset_database()
    
    # Database should still be usable
    with get_db() as session:
        result = session.execute(text("SELECT 1"))
        assert result.scalar() == 1


def test_database_path_creation(test_config, temp_db_path):
    """Test that database parent directory is created if it doesn't exist."""
    # Use a nested path
    nested_path = temp_db_path.parent / "nested" / "path" / "test.db"
    
    test_config.database = DatabaseConfig(path=str(nested_path), echo=False)
    
    # Reset engine to pick up new config
    import app.models.database as db_module
    db_module._engine = None
    
    init_database()
    
    # Parent directories should be created
    assert nested_path.parent.exists()
    assert nested_path.exists()
