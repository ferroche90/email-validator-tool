import asyncio
import random
import string
import time
from typing import Dict, Tuple

import aiosmtplib
import dns.resolver
from email_validator_tool.config import get_settings
from email_validator_tool.core.models import ValidationResult, ValidationStatus
from loguru import logger

from .throttle import enforce_domain_delay

# Throttling handled via validators.throttle module


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

    async def _maybe_await(self, value):
        """Await *value* if it is awaitable, otherwise return it directly."""
        if asyncio.iscoroutine(value):
            return await value
        return value

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

            # If we already have a fresh cached result, we still need to obey
            # the throttling requirement but must avoid a second DNS lookup.
            if self._is_cache_valid(domain):
                await enforce_domain_delay(domain)
                logger.debug(f"Using cached catch-all result for domain: {domain}")
                return self._get_cached_result(domain, email)

            # No valid cache – enforce throttle before performing DNS query.
            await enforce_domain_delay(domain)

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
                mx_server = str(mx_records[0].exchange).rstrip(".")
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
                    port=self.settings.SMTP_PORT,
                    timeout=self.settings.SMTP_TIMEOUT,
                ) as smtp:
                    # Robust against MagicMock (non-awaitable) replacements in unit tests
                    await self._maybe_await(smtp.helo())
                    await self._maybe_await(smtp.mail("test@example.com"))
                    rcpt_result = smtp.rcpt(fake_email)
                    if asyncio.iscoroutine(rcpt_result):
                        response_code, _ = await rcpt_result
                    else:
                        response_code, _ = rcpt_result

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

            except Exception as e:
                # aiosmtplib may raise SMTPException with a tuple like (550, '5.1.1 ...', 'recipient')
                smtp_code = None
                try:
                    smtp_code = int(str(e).lstrip("( ").split(",")[0])
                except Exception:
                    pass

                if smtp_code is not None and 500 <= smtp_code < 600:
                    # Permanent rejection of fake address → domain is NOT catch-all → treat as VALID
                    logger.debug(f"Domain '{domain}' rejected fake email with {smtp_code}, not a catch-all.")
                    result = ValidationResult(email=email, status=ValidationStatus.VALID)
                else:
                    logger.error(f"Error during catch-all SMTP check for {domain}: {e}")
                    result = ValidationResult(
                        email=email,
                        status=ValidationStatus.UNKNOWN_ERROR,
                        details=str(e),
                    )

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
