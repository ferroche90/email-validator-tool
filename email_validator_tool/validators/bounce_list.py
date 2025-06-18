import sqlite3
from pathlib import Path
from loguru import logger
from email_validator_tool.core.models import ValidationResult, ValidationStatus

DB_PATH = Path("bounce_list.db")

def setup_database():
    """Create the bounces table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bounces (
            email TEXT PRIMARY KEY
        )
    """)
    
    conn.commit()
    conn.close()

class BounceListValidator:
    """Validator for checking if an email is in a bounce list"""
    
    def __init__(self, db_path: Path = DB_PATH):
        """Initialize the validator using a local SQLite database."""
        self.db_path = db_path
        setup_database(self.db_path)

    def add_email(self, email: str) -> None:
        """Add an email to the local bounce list."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO bounces (email) VALUES (?)", (email,))
        conn.commit()
        conn.close()
    
    async def validate(self, email: str) -> ValidationResult:
        """
        Check if the email is in a bounce list.
        
        Args:
            email: Email address to validate
            
        Returns:
            ValidationResult with the validation outcome
        """
        try:
            logger.debug(f"Checking if {email} is in bounce list")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM bounces WHERE email = ?", (email,))
            row = cursor.fetchone()
            conn.close()

            if row:
                logger.warning(f"Email {email} is in bounce list")
                return ValidationResult(
                    email=email,
                    status=ValidationStatus.ON_BOUNCE_LIST,
                    details="Email is in bounce list",
                )

            logger.info(f"Email {email} is not in bounce list")
            return ValidationResult(email=email, status=ValidationStatus.VALID)
                        
        except Exception as e:
            logger.error(f"Error validating bounce status for {email}: {str(e)}")
            return ValidationResult(
                email=email,
                status=ValidationStatus.UNKNOWN_ERROR,
                details=str(e)
            )

# Initialize database on module import
setup_database()
