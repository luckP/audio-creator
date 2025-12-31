"""Tests for database initialization and setup."""

from sqlalchemy import text

from app.models.database import init_database, reset_database, get_db
from app.utils.config import DatabaseConfig


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
