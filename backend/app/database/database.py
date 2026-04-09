"""
Database connection and session management for NeuroVision.
Handles PostgreSQL connection pooling and SQLAlchemy setup.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from ..config import settings

# Create database engine with connection pooling
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using them
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Dependency provider for database sessions in FastAPI routes.
    Ensures proper cleanup after each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
