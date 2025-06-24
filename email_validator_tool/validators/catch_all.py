import asyncio
import random
import string

import aiosmtplib
import dns.resolver
from loguru import logger

from email_validator_tool.config import get_settings
from email_validator_tool.core.models import ValidationResult, ValidationStatus


def generate_random_string(k: int = 20) -> str:
    """Generate a random string of lowercase letters and digits."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=k))


class CatchAllValidator:
    """Validator for detecting catch-all domains"""

    def __init__(self):
        """Initialize the validator"""
        self.settings = get_settings()

    async def validate(self, email: str) -> ValidationResult:
        """
        Check if the domain is a catch-all domain.

        Args:
            email: Email address to validate

        Returns:
            ValidationResult with the validation outcome
        """
        try:
            domain = email.split("@")[1]
            logger.debug(f"Checking catch-all status for domain: {domain}")

            # Generate a random, non-existent email address
            fake_email = f"{generate_random_string()}@{domain}"

            # Get MX records for the domain
            try:
                mx_records = dns.resolver.resolve(domain, "MX")
                if not mx_records:
                    return ValidationResult(
                        email=email,
                        status=ValidationStatus.INVALID_MX,
                        details="No MX records found for catch-all check",
                    )
                mx_server = str(mx_records[0].exchange)
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
                    details="No MX records found for catch-all check",
                )

            try:
                async with aiosmtplib.SMTP(
                    hostname=mx_server,
                    port=25,
                    timeout=self.settings.SMTP_TIMEOUT,
                ) as smtp:
                    await smtp.helo()
                    await smtp.mail("test@example.com")
                    response_code, _ = await smtp.rcpt(fake_email)

                    if response_code == 250:
                        logger.warning(
                            f"Domain '{domain}' appears to be a catch-all (accepted fake email)."
                        )
                        return ValidationResult(
                            email=email,
                            status=ValidationStatus.CATCH_ALL,
                            details="Domain accepted a randomly generated, non-existent email address.",
                        )
                    else:
                        # If the fake email is rejected, it's not a catch-all. This is good.
                        return ValidationResult(
                            email=email, status=ValidationStatus.VALID
                        )

            except (aiosmtplib.SMTPConnectError, asyncio.TimeoutError):
                logger.warning(f"Connection failed to {mx_server} for catch-all check.")
                return ValidationResult(
                    email=email,
                    status=ValidationStatus.UNKNOWN_ERROR,
                    details=f"SMTP connection to {mx_server} failed.",
                )
            except Exception as e:
                logger.error(f"Error during catch-all SMTP check for {domain}: {e}")
                return ValidationResult(
                    email=email, status=ValidationStatus.UNKNOWN_ERROR, details=str(e)
                )

        except IndexError:
            return ValidationResult(
                email=email,
                status=ValidationStatus.INVALID_SYNTAX,
                details="Malformed email address",
            )
        except Exception as e:
            logger.error(f"Error during catch-all validation for {email}: {e}")
            return ValidationResult(
                email=email, status=ValidationStatus.UNKNOWN_ERROR, details=str(e)
            )
