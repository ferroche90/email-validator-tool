from loguru import logger
from disposable_email_domains import blocklist
from email_validator_tool.core.models import ValidationResult, ValidationStatus

class DisposableValidator:
    """
    Validator for disposable email domains using a local dataset.
    """

    async def validate(self, email: str) -> ValidationResult:
        """
        Check if the email domain is from a known disposable email provider.

        Args:
            email: Email address to validate.

        Returns:
            ValidationResult with the validation outcome.
        """
        try:
            domain = email.split('@')[1]
            logger.debug(f"Checking if domain '{domain}' is disposable.")

            # Check if domain is in the blocklist
            if domain in blocklist:
                logger.warning(f"Domain '{domain}' is disposable.")
                return ValidationResult(
                    email=email,
                    status=ValidationStatus.DISPOSABLE,
                    details="Domain is from a known disposable email provider."
                )

            # If not disposable, it passes this specific validation check
            return ValidationResult(
                email=email,
                status=ValidationStatus.VALID
            )

        except IndexError:
            # This handles cases where the email format is malformed (no '@')
            logger.error(f"Could not extract domain from '{email}'.")
            return ValidationResult(
                email=email,
                status=ValidationStatus.INVALID_SYNTAX,
                details="Malformed email address, cannot extract domain."
            )
        except Exception as e:
            logger.error(f"An unexpected error occurred in DisposableValidator for {email}: {e}")
            return ValidationResult(
                email=email,
                status=ValidationStatus.UNKNOWN_ERROR,
                details=f"Unexpected error: {str(e)}"
            )