import random
import string
import aiosmtplib
import dns.resolver
from email.mime.text import MIMEText
from loguru import logger
from email_validator_tool.core.models import ValidationResult, ValidationStatus
from email_validator_tool.config import Settings


def generate_random_email(domain: str) -> str:
    """Generate a random email address for the given domain."""
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
    return f"{random_string}@{domain}"

class CatchAllValidator:
    """Validator for checking if a domain has catch-all enabled"""
    
    def __init__(self):
        """Initialize the validator without external API."""
        self.settings = Settings()
    
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
            
            if not self.settings.ENABLE_CATCH_ALL:
                logger.debug("Catch-all check disabled in settings")
                return ValidationResult(email=email, status=ValidationStatus.VALID)

            try:
                mx_records = dns.resolver.resolve(domain, 'MX')
                if not mx_records:
                    return ValidationResult(
                        email=email,
                        status=ValidationStatus.INVALID_MX,
                        details="No MX records found",
                    )
            except dns.resolver.NXDOMAIN:
                return ValidationResult(
                    email=email,
                    status=ValidationStatus.INVALID_DOMAIN,
                    details="Domain does not exist",
                )
            except dns.resolver.NoAnswer:
                return ValidationResult(
                    email=email,
                    status=ValidationStatus.INVALID_MX,
                    details="No MX records found",
                )

            mx_host = str(mx_records[0].exchange)
            random_email = generate_random_email(domain)

            try:
                async with aiosmtplib.SMTP(
                    hostname=mx_host,
                    port=self.settings.SMTP_PORT,
                    timeout=self.settings.SMTP_TIMEOUT,
                ) as smtp:
                    await smtp.ehlo()
                    await smtp.mail(f"verify@{domain}")
                    response = await smtp.rcpt(random_email)
                    if response.code == 250:
                        logger.warning(f"Domain {domain} has catch-all enabled")
                        return ValidationResult(
                            email=email,
                            status=ValidationStatus.CATCH_ALL,
                            details="Domain has catch-all enabled",
                        )
                    elif response.code == 550:
                        logger.info(f"Domain {domain} does not have catch-all enabled")
                        return ValidationResult(email=email, status=ValidationStatus.VALID)
                    else:
                        return ValidationResult(
                            email=email,
                            status=ValidationStatus.UNKNOWN_ERROR,
                            details=f"Unexpected SMTP code {response.code}",
                        )
            except aiosmtplib.SMTPException as exc:
                logger.error(f"SMTP error during catch-all check: {exc}")
                return ValidationResult(
                    email=email,
                    status=ValidationStatus.UNKNOWN_ERROR,
                    details=f"SMTP error: {str(exc)}",
                )
                        
        except Exception as e:
            logger.error(f"Error validating catch-all status for {email}: {str(e)}")
            return ValidationResult(
                email=email,
                status=ValidationStatus.UNKNOWN_ERROR,
                details=str(e)
            )
