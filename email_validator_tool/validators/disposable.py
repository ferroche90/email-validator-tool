import aiohttp
from loguru import logger
from email_validator_tool.core.models import ValidationResult, ValidationStatus

class DisposableValidator:
    """Validator for disposable email domains"""
    
    def __init__(self):
        """Initialize the validator"""
        self.api_url = "https://disposable.debounce.io/v1/disposable"
        self.api_key = None  # Set your API key here
    
    async def validate(self, email: str) -> ValidationResult:
        """
        Check if the email domain is disposable.
        
        Args:
            email: Email address to validate
            
        Returns:
            ValidationResult with the validation outcome
        """
        try:
            domain = email.split('@')[1]
            logger.debug(f"Checking if domain {domain} is disposable")
            
            async with aiohttp.ClientSession() as session:
                params = {'email': email}
                if self.api_key:
                    params['api_key'] = self.api_key
                    
                async with session.get(self.api_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('disposable'):
                            logger.warning(f"Domain {domain} is disposable")
                            return ValidationResult(
                                email=email,
                                status=ValidationStatus.DISPOSABLE,
                                details={"reason": "Domain is disposable"}
                            )
                        logger.info(f"Domain {domain} is not disposable")
                        return ValidationResult(
                            email=email,
                            status=ValidationStatus.VALID
                        )
                    else:
                        logger.error(f"Error checking disposable status: {response.status}")
                        return ValidationResult(
                            email=email,
                            status=ValidationStatus.UNKNOWN_ERROR,
                            details={"error": f"API error: {response.status}"}
                        )
                        
        except Exception as e:
            logger.error(f"Error validating disposable status for {email}: {str(e)}")
            return ValidationResult(
                email=email,
                status=ValidationStatus.UNKNOWN_ERROR,
                details={"error": str(e)}
            )
