"""Database initialization script."""

import logging
from app.models import init_database
from app.utils.logger import get_logger

logger = get_logger("init_db")

def init_db() -> None:
    """
    Initialize the database by creating all tables.
    """
    logger.info("Creating database tables...")
    init_database()
    logger.info("Database initialized successfully.")

def reset_db() -> None:
    """
    Reset the database (drop all tables and recreate).
    """
    from app.models.database import reset_database
    logger.warning("Resetting database - ALL DATA WILL BE LOST!")
    reset_database()
    logger.info("Database reset successfully.")

if __name__ == "__main__":
    init_db()
