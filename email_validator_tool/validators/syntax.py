from email_validator import validate_email, EmailNotValidError
from loguru import logger
from email_validator_tool.core.models import ValidationResult, ValidationStatus

async def check(email: str) -> ValidationResult:
    try:
        # Validate email syntax
        validated = validate_email(email)
        logger.info(f"Email {email} has valid syntax")
        return ValidationResult(
            email=email,
            status=ValidationStatus.VALID
        )
    except EmailNotValidError as e:
        logger.warning(f"Invalid email syntax for {email}: {str(e)}")
        return ValidationResult(
            email=email,
            status=ValidationStatus.INVALID_SYNTAX,
            details=f"Invalid email syntax: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error validating email syntax for {email}: {str(e)}")
        return ValidationResult(
            email=email,
            status=ValidationStatus.UNKNOWN_ERROR,
            details=f"Syntax validation error: {str(e)}"
        )
