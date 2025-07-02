import os
from typing import Generator
from urllib.parse import urlparse
from pathlib import Path

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

# ---------------------------------------------------------------------------
# Database configuration
# ---------------------------------------------------------------------------
# We want a single SQLite file during local development.  Place it in the
# project-level `data/` directory so it is not confused with source files and
# remains consistent no matter where the application is launched from.
#
#  • Default location: {PROJECT_ROOT}/data/app.db
#  • Environment variable `DATABASE_URL` can override this if desired.
#
# Compute the absolute path to the project root (= three levels up from this
# file: backend/app/database/database.py -> backend/app/database -> backend/app
# -> backend  -> project root).
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Ensure the data directory exists
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Assemble default SQLite URL
default_sqlite_url = f"sqlite:///{DATA_DIR / 'app.db'}"

# Read from environment or fall back to default
DATABASE_URL = os.getenv("DATABASE_URL", default_sqlite_url)
# ---------------------------------------------------------------------------

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
