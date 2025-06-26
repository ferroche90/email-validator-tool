import asyncio
import random
import string
import time
from typing import Dict, Tuple

import aiosmtplib
import dns.resolver
from loguru import logger

from email_validator_tool.config import get_settings
from email_validator_tool.core.models import ValidationResult, ValidationStatus

# Shared throttle dict with SMTPValidator
_last_contact: Dict[str, float] = {}

def generate_random_string(k: int = 20) -> str:
    """Generate a random string of lowercase letters and digits."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=k))


class CatchAllValidator:
    """Validator for detecting catch-all domains with caching and throttling"""

    def __init__(self):
        """Initialize the validator"""
        self.settings = get_settings()
        self.domain_cache: Dict[str, Tuple[ValidationResult, float]] = {}

    def _is_cache_valid(self, domain: str) -> bool:
        """Check if cached result for domain is still valid."""
        if domain not in self.domain_cache:
            return False
        
        _, timestamp = self.domain_cache[domain]
        return time.time() - timestamp < self.settings.CATCH_ALL_CACHE_TTL_SECONDS

    def _get_cached_result(self, domain: str, email: str) -> ValidationResult:
        """Get cached result for domain, updating email field."""
        cached_result, _ = self.domain_cache[domain]
        return ValidationResult(
            email=email,
            status=cached_result.status,
            details=cached_result.details,
        )

    def _cache_result(self, domain: str, result: ValidationResult):
        """Cache result for domain."""
        self.domain_cache[domain] = (result, time.time())

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

            # Check cache first
            if self._is_cache_valid(domain):
                logger.debug(f"Using cached catch-all result for domain: {domain}")
                return self._get_cached_result(domain, email)

            # Check and enforce delay between requests to the same domain
            current_time = time.time()
            if domain in _last_contact:
                time_since_last = current_time - _last_contact[domain]
                if time_since_last < self.settings.PER_DOMAIN_DELAY_SECONDS:
                    delay = self.settings.PER_DOMAIN_DELAY_SECONDS - time_since_last
                    logger.debug(f"Waiting {delay:.1f}s before checking catch-all for {domain}")
                    await asyncio.sleep(delay)

            # Update last contact time
            _last_contact[domain] = time.time()

            # Generate a random, non-existent email address
            fake_email = f"{generate_random_string()}@{domain}"

            # Get MX records for the domain
            try:
                mx_records = dns.resolver.resolve(domain, "MX")
                if not mx_records:
                    result = ValidationResult(
                        email=email,
                        status=ValidationStatus.INVALID_MX,
                        details="No MX records found for catch-all check",
                    )
                    self._cache_result(domain, result)
                    return result
                mx_server = str(mx_records[0].exchange)
            except dns.resolver.NXDOMAIN:
                result = ValidationResult(
                    email=email,
                    status=ValidationStatus.INVALID_DOMAIN,
                    details="Domain does not exist",
                )
                self._cache_result(domain, result)
                return result
            except dns.resolver.NoAnswer:
                result = ValidationResult(
                    email=email,
                    status=ValidationStatus.INVALID_MX,
                    details="No MX records found for catch-all check",
                )
                self._cache_result(domain, result)
                return result

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
                        logger.warning(f"Domain '{domain}' appears to be a catch-all (accepted fake email).")
                        result = ValidationResult(
                            email=email,
                            status=ValidationStatus.CATCH_ALL,
                            details="Domain accepted a randomly generated, non-existent email address.",
                        )
                        self._cache_result(domain, result)
                        return result
                    else:
                        # If the fake email is rejected, it's not a catch-all. This is good.
                        result = ValidationResult(email=email, status=ValidationStatus.VALID)
                        self._cache_result(domain, result)
                        return result

            except (aiosmtplib.SMTPConnectError, asyncio.TimeoutError):
                logger.warning(f"Connection failed to {mx_server} for catch-all check.")
                result = ValidationResult(
                    email=email,
                    status=ValidationStatus.UNKNOWN_ERROR,
                    details=f"SMTP connection to {mx_server} failed.",
                )
                self._cache_result(domain, result)
                return result
            except Exception as e:
                logger.error(f"Error during catch-all SMTP check for {domain}: {e}")
                result = ValidationResult(email=email, status=ValidationStatus.UNKNOWN_ERROR, details=str(e))
                self._cache_result(domain, result)
                return result

        except IndexError:
            result = ValidationResult(
                email=email,
                status=ValidationStatus.INVALID_SYNTAX,
                details="Malformed email address",
            )
            return result
        except Exception as e:
            logger.error(f"Error during catch-all validation for {email}: {e}")
            result = ValidationResult(email=email, status=ValidationStatus.UNKNOWN_ERROR, details=str(e))
            return result
