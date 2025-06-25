"""
Role account validator.
"""

from loguru import logger

from email_validator_tool.constants import COMMON_ROLE_ACCOUNTS
from email_validator_tool.core.models import ValidationResult, ValidationStatus


class RoleAccountValidator:
    """Validator for role-based email accounts"""

    def __init__(self):
        """Initialize the validator"""
        pass

    async def validate(self, email: str) -> ValidationResult:
        """
        Check if the email is a role-based account.

        Args:
            email: Email address to validate

        Returns:
            ValidationResult with the validation outcome
        """
        try:
            local_part = email.split("@")[0].lower()
            logger.debug(f"Checking if {local_part} is a role account")

            if local_part in COMMON_ROLE_ACCOUNTS:
                logger.warning(f"Email {email} is a role account")
                return ValidationResult(
                    email=email,
                    status=ValidationStatus.ROLE_ACCOUNT,
                    details=f"Local part '{local_part}' is a role account",
                )

            logger.info(f"Email {email} is not a role account")
            return ValidationResult(email=email, status=ValidationStatus.VALID)

        except Exception as e:
            logger.error(f"Error validating role account status for {email}: {str(e)}")
            return ValidationResult(email=email, status=ValidationStatus.UNKNOWN_ERROR, details=str(e))
