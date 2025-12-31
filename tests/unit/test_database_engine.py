"""Tests for database engine and session factory."""

from app.models.database import get_engine, get_session_factory


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
