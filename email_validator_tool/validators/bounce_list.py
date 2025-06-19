import sqlite3
import asyncio
from pathlib import Path
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

# --- Database check function (blocking) ---
def _check_email_in_db(email: str) -> bool:
    """
    Checks if a single email exists in the SQLite database.
    This is a synchronous, blocking function.
    """
    conn = None # Ensure conn is defined
    try:
        conn = sqlite3.connect(DB_PATH, timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM bounces WHERE email = ?", (email,))
        result = cursor.fetchone()
        return result is not None
    except sqlite3.Error as e:
        logger.error(f"Database error while checking {email}: {e}")
        return False # Assume not on list if DB fails
    finally:
        if conn:
            conn.close()

class BounceListValidator:
    """
    Validator for checking if an email is in a local SQLite bounce list.
    """

    async def validate(self, email: str) -> ValidationResult:
        """
        Check if the email is in the local bounce list database.

        Args:
            email: Email address to validate.

        Returns:
            ValidationResult with the validation outcome.
        """
        try:
            logger.debug(f"Checking local bounce list for {email}.")

            # Run the synchronous DB check in a separate thread to avoid blocking asyncio
            is_bounced = await asyncio.to_thread(_check_email_in_db, email)

            if is_bounced:
                logger.warning(f"Email {email} found in local bounce list.")
                return ValidationResult(
                    email=email,
                    status=ValidationStatus.ON_BOUNCE_LIST,
                    details="Email is on the local bounce list."
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