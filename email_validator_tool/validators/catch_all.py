import random
import string
import aiosmtplib
import aiohttp
from email.mime.text import MIMEText
from loguru import logger
from email_validator_tool.core.models import ValidationResult, ValidationStatus
from email_validator_tool.config import Settings

SETTINGS = Settings()

def generate_random_email(domain: str) -> str:
    """Generate a random email address for the given domain."""
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
    return f"{random_string}@{domain}"

class CatchAllValidator:
    """Validator for checking if a domain has catch-all enabled"""
    
    def __init__(self):
        """Initialize the validator"""
        self.api_url = "https://catchall.debounce.io/v1/catchall"
        self.api_key = None  # Set your API key here
    
    async def validate(self, email: str) -> ValidationResult:
        """
        Check if the domain has catch-all enabled.
        
        Args:
            email: Email address to validate
            
        Returns:
            ValidationResult with the validation outcome
        """
        try:
            domain = email.split('@')[1]
            logger.debug(f"Checking if domain {domain} has catch-all enabled")
            
            async with aiohttp.ClientSession() as session:
                params = {'email': email}
                if self.api_key:
                    params['api_key'] = self.api_key
                    
                async with session.get(self.api_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('catchall'):
                            logger.warning(f"Domain {domain} has catch-all enabled")
                            return ValidationResult(
                                email=email,
                                status=ValidationStatus.CATCH_ALL,
                                details="Domain has catch-all enabled"
                            )
                        logger.info(f"Domain {domain} does not have catch-all enabled")
                        return ValidationResult(
                            email=email,
                            status=ValidationStatus.VALID
                        )
                    else:
                        logger.error(f"Error checking catch-all status: {response.status}")
                        return ValidationResult(
                            email=email,
                            status=ValidationStatus.UNKNOWN_ERROR,
                            details=f"API error: {response.status}"
                        )
                        
        except Exception as e:
            logger.error(f"Error validating catch-all status for {email}: {str(e)}")
            return ValidationResult(
                email=email,
                status=ValidationStatus.UNKNOWN_ERROR,
                details=str(e)
            )
