import sqlite3
from pathlib import Path
from email_validator_tool.core.models import ValidationResult, ValidationStatus
import aiohttp
from loguru import logger

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
    
    def __init__(self):
        """Initialize the validator"""
        self.api_url = "https://bounce.debounce.io/v1/bounce"
        self.api_key = None  # Set your API key here
    
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
            
            async with aiohttp.ClientSession() as session:
                params = {'email': email}
                if self.api_key:
                    params['api_key'] = self.api_key
                    
                async with session.get(self.api_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('bounce'):
                            logger.warning(f"Email {email} is in bounce list")
                            return ValidationResult(
                                email=email,
                                status=ValidationStatus.ON_BOUNCE_LIST,
                                details="Email is in bounce list"
                            )
                        logger.info(f"Email {email} is not in bounce list")
                        return ValidationResult(
                            email=email,
                            status=ValidationStatus.VALID
                        )
                    else:
                        logger.error(f"Error checking bounce status: {response.status}")
                        return ValidationResult(
                            email=email,
                            status=ValidationStatus.UNKNOWN_ERROR,
                            details=f"API error: {response.status}"
                        )
                        
        except Exception as e:
            logger.error(f"Error validating bounce status for {email}: {str(e)}")
            return ValidationResult(
                email=email,
                status=ValidationStatus.UNKNOWN_ERROR,
                details=str(e)
            )

# Initialize database on module import
setup_database()
