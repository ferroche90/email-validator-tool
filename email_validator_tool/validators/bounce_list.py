import sqlite3
import asyncio
from pathlib import Path
from typing import Set
from loguru import logger
from email_validator_tool.core.models import ValidationResult, ValidationStatus

DB_PATH = Path("bounce_list.db")

def setup_database():
    """Create the bounces table if it doesn't exist."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bounces (
                email TEXT PRIMARY KEY
            )
        """)
        conn.commit()
        conn.close()
        logger.info(f"Database '{DB_PATH}' setup complete.")
    except sqlite3.Error as e:
        logger.critical(f"Failed to set up SQLite database: {e}")

def load_bounce_list() -> Set[str]:
    """
    Load all bounce emails from the database into a Python set.
    
    Returns:
        Set containing all bounce emails
    """
    bounce_set = set()
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM bounces")
        rows = cursor.fetchall()
        
        for row in rows:
            bounce_set.add(row[0])
        
        logger.info(f"Loaded {len(bounce_set)} bounce emails into memory")
        return bounce_set
        
    except sqlite3.Error as e:
        logger.error(f"Failed to load bounce list from database: {e}")
        return set()
    finally:
        if conn:
            conn.close()

class BounceListValidator:
    """
    Validator for checking if an email is in a local SQLite bounce list.
    Optimized to load the entire bounce list into memory for fast lookups.
    """

    def __init__(self):
        """Initialize the validator by loading the bounce list into memory."""
        self.bounce_set = load_bounce_list()
        logger.info(f"BounceListValidator initialized with {len(self.bounce_set)} emails in memory")

    def reload_bounce_list(self) -> int:
        """
        Reload the bounce list from the database.
        
        Returns:
            Number of bounce emails loaded
        """
        self.bounce_set = load_bounce_list()
        return len(self.bounce_set)

    def get_bounce_count(self) -> int:
        """
        Get the current number of bounce emails in memory.
        
        Returns:
            Number of bounce emails
        """
        return len(self.bounce_set)

    async def validate(self, email: str) -> ValidationResult:
        """
        Check if the email is in the in-memory bounce list.

        Args:
            email: Email address to validate.

        Returns:
            ValidationResult with the validation outcome.
        """
        try:
            logger.debug(f"Checking in-memory bounce list for {email}.")

            # Simple synchronous set lookup - no I/O operations
            if email in self.bounce_set:
                logger.warning(f"Email {email} found in bounce list.")
                return ValidationResult(
                    email=email,
                    status=ValidationStatus.ON_BOUNCE_LIST,
                    details="Email is on the bounce list."
                )

            return ValidationResult(
                email=email,
                status=ValidationStatus.VALID
            )

        except Exception as e:
            logger.error(f"An unexpected error occurred in BounceListValidator for {email}: {e}")
            return ValidationResult(
                email=email,
                status=ValidationStatus.UNKNOWN_ERROR,
                details=f"Unexpected error: {str(e)}"
            )

# Initialize database on module import
setup_database()