import sqlite3
from pathlib import Path
from email_validator_tool.models import ValidationResult, ValidationStatus

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

async def check(email: str) -> ValidationResult:
    """Check if the email exists in the bounce list database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM bounces WHERE email = ?", (email,))
        exists = cursor.fetchone() is not None
        
        conn.close()
        
        if exists:
            return ValidationResult(
                email=email,
                status=ValidationStatus.ON_BOUNCE_LIST,
                details="Email found in bounce list database"
            )
        
        return ValidationResult(
            email=email,
            status=ValidationStatus.VALID
        )
        
    except sqlite3.Error as e:
        return ValidationResult(
            email=email,
            status=ValidationStatus.UNKNOWN_ERROR,
            details=f"Database error: {str(e)}"
        )

# Initialize database on module import
setup_database()
