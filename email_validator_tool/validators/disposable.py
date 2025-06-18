from loguru import logger
from email_validator_tool.core.models import ValidationResult, ValidationStatus

class DisposableValidator:
    """Validator for disposable email domains."""

    def __init__(self):
        """Initialize the validator without requiring any API."""
        self.disposable_domains = {
            "mailinator.com",
            "tempmail.com",
            "10minutemail.com",
            "throwawaymail.com",
            "guerrillamail.com",
            "trashmail.com",
            "yopmail.com",
            "maildrop.cc",
            "getnada.com",
        }
    
    async def validate(self, email: str) -> ValidationResult:
        """
        Check if the email domain is disposable.
        
        Args:
            email: Email address to validate
            
        Returns:
            ValidationResult with the validation outcome
        """
        try:
            domain = email.split('@')[1].lower()
            logger.debug(f"Checking if domain {domain} is disposable")
            if domain in self.disposable_domains:
                logger.warning(f"Domain {domain} is disposable")
                return ValidationResult(
                    email=email,
                    status=ValidationStatus.DISPOSABLE,
                    details="Domain is disposable",
                )

            logger.info(f"Domain {domain} is not disposable")
            return ValidationResult(email=email, status=ValidationStatus.VALID)
            
                        
        except Exception as e:
            logger.error(f"Error validating disposable status for {email}: {str(e)}")
            return ValidationResult(
                email=email,
                status=ValidationStatus.UNKNOWN_ERROR,
                details=str(e)
            )
