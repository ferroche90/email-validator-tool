from email_validator import validate_email, EmailNotValidError
from loguru import logger
from email_validator_tool.models import ValidationResult, ValidationStatus

async def check(email: str) -> ValidationResult:
    try:
        validate_email(email, allow_smtputf8=False)
        return ValidationResult(
            email=email,
            status=ValidationStatus.VALID
        )
    except EmailNotValidError as exc:
        logger.debug(f"Syntax invalid for {email}: {exc}")
        return ValidationResult(
            email=email,
            status=ValidationStatus.INVALID_SYNTAX,
            details=str(exc)
        )
