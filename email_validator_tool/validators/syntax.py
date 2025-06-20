from email_validator import validate_email, EmailNotValidError
from loguru import logger
from email_validator_tool.core.models import ValidationResult, ValidationStatus

class SyntaxValidator:
    """Validator for email syntax"""
    
    async def validate(self, email: str) -> ValidationResult:
        try:
            # Validate email syntax
            validated = validate_email(email)
            logger.info(f"Email {email} has valid syntax")
            return ValidationResult(
                email=email,
                status=ValidationStatus.VALID
            )
        except EmailNotValidError as e:
            error_message = str(e)
            # Check for domain-related errors in the message
            domain_error_keywords = [
                'The domain name',
                'DNS',
                'does not exist',
                'domain part',
                'No MX record',
                'not a valid domain',
            ]
            if any(keyword.lower() in error_message.lower() for keyword in domain_error_keywords):
                logger.warning(f"Invalid domain for {email}: {error_message}")
                return ValidationResult(
                    email=email,
                    status=ValidationStatus.INVALID_DOMAIN,
                    details=f"Invalid domain: {error_message}"
                )
            else:
                logger.warning(f"Invalid email syntax for {email}: {error_message}")
                return ValidationResult(
                    email=email,
                    status=ValidationStatus.INVALID_SYNTAX,
                    details=f"Invalid email syntax: {error_message}"
                )
        except Exception as e:
            logger.error(f"Error validating email syntax for {email}: {str(e)}")
            return ValidationResult(
                email=email,
                status=ValidationStatus.UNKNOWN_ERROR,
                details=f"Syntax validation error: {str(e)}"
            )
