import os
from typing import Generator
from urllib.parse import urlparse

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

# Database URL from environment (default: ./app.db inside backend directory)
# Ensure that the directory for a SQLite file-based database exists before the
# engine tries to connect. This prevents `sqlite3.OperationalError: unable to
# open database file` when the parent directory is missing.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# If we're using SQLite, make sure the directory for the DB file exists.
parsed = urlparse(DATABASE_URL)
if parsed.scheme == "sqlite":
    db_path = parsed.path
    # On Windows the parsed path can start with a leading slash (e.g. "/C:/...")
    if db_path.startswith("/"):
        db_path = db_path[1:]

    # Skip in-memory databases (":memory:") and edge cases with empty path
    if db_path and db_path != ":memory:":
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

# Handle PostgreSQL URL format for cloud platforms (Render, Railway, etc.)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine with appropriate configuration for SQLite vs PostgreSQL
if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=os.getenv("DEBUG", "false").lower() == "true",
    )
else:
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,  # Recycle connections every 5 minutes
        echo=os.getenv("DEBUG", "false").lower() == "true",
    )


def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    with Session(engine) as session:
        yield session
