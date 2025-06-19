import random
import string
import asyncio
import dns.resolver
import aiosmtplib
from loguru import logger
from email_validator_tool.core.models import ValidationResult, ValidationStatus
from email_validator_tool.config import Settings

SETTINGS = Settings()

def generate_random_string(k: int = 20) -> str:
    """Generate a random string of lowercase letters and digits."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=k))

class CatchAllValidator:
    """
    Validator for checking if a domain has catch-all enabled via SMTP check.
    """

    async def validate(self, email: str) -> ValidationResult:
        """
        Check if the domain has catch-all enabled by testing a fake email address.

        Args:
            email: Email address to validate.

        Returns:
            ValidationResult with the validation outcome.
        """
        try:
            domain = email.split('@')[1]
            logger.debug(f"Checking if domain '{domain}' has catch-all enabled.")
        except IndexError:
            return ValidationResult(email=email, status=ValidationStatus.INVALID_SYNTAX, details="Malformed email.")

        # 1. Get MX record for the domain
        try:
            mx_records = await asyncio.to_thread(dns.resolver.resolve, domain, 'MX')
            mx_server = str(mx_records[0].exchange)
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            logger.warning(f"No MX records for {domain}, cannot check for catch-all.")
            return ValidationResult(email=email, status=ValidationStatus.INVALID_MX)
        except Exception as e:
            logger.error(f"DNS query failed for {domain}: {e}")
            return ValidationResult(email=email, status=ValidationStatus.UNKNOWN_ERROR, details=f"DNS error: {e}")

        # 2. Perform SMTP check with a fake email
        fake_email = f"{generate_random_string()}@{domain}"
        try:
            async with aiosmtplib.SMTP(
                hostname=mx_server,
                port=25,
                timeout=SETTINGS.SMTP_TIMEOUT,
            ) as smtp:
                await smtp.helo()
                await smtp.mail("test@example.com")
                response_code, _ = await smtp.rcpt(fake_email)

                if response_code == 250:
                    logger.warning(f"Domain '{domain}' appears to be a catch-all (accepted fake email).")
                    return ValidationResult(
                        email=email,
                        status=ValidationStatus.CATCH_ALL,
                        details="Domain accepted a randomly generated, non-existent email address."
                    )
                else:
                    # If the fake email is rejected, it's not a catch-all. This is good.
                    return ValidationResult(email=email, status=ValidationStatus.VALID)

        except (aiosmtplib.SMTPConnectError, asyncio.TimeoutError):
             logger.warning(f"Connection failed to {mx_server} for catch-all check.")
             return ValidationResult(email=email, status=ValidationStatus.UNKNOWN_ERROR, details=f"SMTP connection to {mx_server} failed.")
        except Exception as e:
            logger.error(f"Error during catch-all SMTP check for {domain}: {e}")
            return ValidationResult(email=email, status=ValidationStatus.UNKNOWN_ERROR, details=str(e))