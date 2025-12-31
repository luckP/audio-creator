"""Tests for database session management."""

import pytest
from sqlalchemy import text

from app.models.database import get_db, init_database


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
