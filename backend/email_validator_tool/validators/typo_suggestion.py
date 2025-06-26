from email_validator_tool.core.models import ValidationResult, ValidationStatus
from email_validator_tool.core.typo_suggestions import suggest_domain
from loguru import logger


class TypoSuggestionValidator:
    """
    Validator that adds typo suggestions to validation results.
    This validator doesn't change the validation status, only adds suggestions.
    """

    async def validate(self, email: str) -> ValidationResult:
        """
        Add typo suggestions to the validation result.
        
        Args:
            email: Email address to validate
            
        Returns:
            ValidationResult with optional typo suggestion
        """
        try:
            # Extract domain from email
            if "@" not in email:
                return ValidationResult(email=email, status=ValidationStatus.VALID)
            
            domain = email.split("@")[1]
            
            # Get typo suggestion
            suggestion = suggest_domain(domain)
            
            if suggestion:
                # Create email with suggested domain
                suggested_email = f"{email.split('@')[0]}@{suggestion}"
                return ValidationResult(
                    email=email,
                    status=ValidationStatus.VALID,
                    suggestion=suggested_email
                )
            
            return ValidationResult(email=email, status=ValidationStatus.VALID)
            
        except Exception as e:
            logger.error(f"Error in TypoSuggestionValidator for {email}: {e}")
            return ValidationResult(email=email, status=ValidationStatus.VALID) 