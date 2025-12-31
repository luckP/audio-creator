"""Database engine and session management."""

from pathlib import Path
from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase

from ..utils.config import get_config


# Base class for all models
class Base(DeclarativeBase):
    """Base class for all database models."""
    pass

# Global engine and session factory (singletons)
_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None


def get_engine() -> Engine:
    """
    Get or create database engine.
    
    Returns:
        Engine: SQLAlchemy database engine
        
    Note:
        This is a singleton - the engine is created once and reused.
    """
    global _engine
    if _engine is None:
        config = get_config()
        db_path = Path(config.database.path)
        
        # Ensure parent directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        db_url = f"sqlite:///{db_path}"
        _engine = create_engine(
            db_url,
            echo=config.database.echo,  # pylint: disable=no-member
            connect_args={"check_same_thread": False},  # Needed for SQLite
            pool_pre_ping=True,  # Verify connections before using
        )
    return _engine


def get_session_factory() -> sessionmaker:
    """
    Get or create session factory.
    
    Returns:
        sessionmaker: SQLAlchemy session factory
        
    Note:
        This is a singleton - the factory is created once and reused.
    """
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
    return _SessionLocal


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Get database session context manager.
    
    Yields:
        Session: SQLAlchemy session
        
    Example:
        >>> with get_db() as db:
        ...     documents = db.query(Document).all()
        
    Note:
        The session is automatically closed when the context exits.
        Transactions are committed on success, rolled back on error.
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_database() -> None:
    """
    Initialize database - create all tables.
    
    Note:
        This creates all tables defined by models that inherit from Base.
        Safe to call multiple times - won't recreate existing tables.
    """
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def reset_database() -> None:
    """
    Reset database - drop and recreate all tables.
    
    Warning:
        This will DELETE ALL DATA in the database!
        Only use for testing or development.
    """
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
