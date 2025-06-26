import sqlite3
from pathlib import Path
from typing import Set

from loguru import logger

from email_validator_tool.core.models import ValidationResult, ValidationStatus
from email_validator_tool.utils.paths import get_data_dir

# Update SUPPRESSION_DB_PATH to use the data directory
SUPPRESSION_DB_PATH = get_data_dir() / "suppression_list.db"


def setup_suppression_database():
    """Create the suppressions table if it doesn't exist."""
    try:
        conn = sqlite3.connect(str(SUPPRESSION_DB_PATH))
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS suppressions (
                email TEXT PRIMARY KEY,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        conn.commit()
        conn.close()
        logger.info(f"Suppression database '{SUPPRESSION_DB_PATH}' setup complete.")
    except sqlite3.Error as e:
        logger.critical(f"Failed to set up suppression SQLite database: {e}")


def load_suppression_list() -> Set[str]:
    """
    Load all suppressed emails from the database into a Python set.

    Returns:
        Set containing all suppressed emails
    """
    suppression_set = set()
    conn = None
    try:
        conn = sqlite3.connect(str(SUPPRESSION_DB_PATH), timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM suppressions")
        rows = cursor.fetchall()

        for row in rows:
            suppression_set.add(row[0])

        logger.info(f"Loaded {len(suppression_set)} suppressed emails into memory")
        return suppression_set

    except sqlite3.Error as e:
        logger.error(f"Failed to load suppression list from database: {e}")
        return set()
    finally:
        if conn:
            conn.close()


def add_suppressions(emails: Set[str]) -> int:
    """
    Add emails to the suppression database.

    Args:
        emails: Set of email addresses to suppress

    Returns:
        Number of emails successfully added
    """
    if not emails:
        return 0

    conn = None
    added_count = 0
    try:
        conn = sqlite3.connect(str(SUPPRESSION_DB_PATH), timeout=10)
        cursor = conn.cursor()
        
        for email in emails:
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO suppressions (email) VALUES (?)",
                    (email.lower(),)
                )
                if cursor.rowcount > 0:
                    added_count += 1
            except sqlite3.Error as e:
                logger.error(f"Failed to add suppression for {email}: {e}")
        
        conn.commit()
        logger.info(f"Added {added_count} new suppressions to database")
        return added_count

    except sqlite3.Error as e:
        logger.error(f"Failed to add suppressions to database: {e}")
        return 0
    finally:
        if conn:
            conn.close()


class SuppressionValidator:
    """
    Validator for checking if an email is in the customer-suppressed list.
    Optimized to load the entire suppression list into memory for fast lookups.
    """

    def __init__(self):
        """Initialize the validator by loading the suppression list into memory."""
        self.suppression_set = load_suppression_list()
        logger.info(f"SuppressionValidator initialized with {len(self.suppression_set)} emails in memory")

    def reload_suppression_list(self) -> int:
        """
        Reload the suppression list from the database.

        Returns:
            Number of suppressed emails loaded
        """
        self.suppression_set = load_suppression_list()
        return len(self.suppression_set)

    def get_suppression_count(self) -> int:
        """
        Get the current number of suppressed emails in memory.

        Returns:
            Number of suppressed emails
        """
        return len(self.suppression_set)

    def add_suppressions(self, emails: Set[str]) -> int:
        """
        Add emails to the suppression list and reload from database.

        Args:
            emails: Set of email addresses to suppress

        Returns:
            Number of emails successfully added
        """
        added_count = add_suppressions(emails)
        if added_count > 0:
            # Reload the list to include new suppressions
            self.reload_suppression_list()
        return added_count

    async def validate(self, email: str) -> ValidationResult:
        """
        Check if the email is in the in-memory suppression list.

        Args:
            email: Email address to validate.

        Returns:
            ValidationResult with the validation outcome.
        """
        try:
            logger.debug(f"Checking in-memory suppression list for {email}.")

            # Simple synchronous set lookup - no I/O operations
            if email.lower() in self.suppression_set:
                logger.warning(f"Email {email} found in suppression list.")
                return ValidationResult(
                    email=email,
                    status=ValidationStatus.SUPPRESSED,
                    details="Email is on the customer suppression list.",
                )

            return ValidationResult(email=email, status=ValidationStatus.VALID)

        except Exception as e:
            logger.error(f"An unexpected error occurred in SuppressionValidator for {email}: {e}")
            return ValidationResult(
                email=email,
                status=ValidationStatus.UNKNOWN_ERROR,
                details=f"Unexpected error: {str(e)}",
            )


# Initialize database on module import
setup_suppression_database() 