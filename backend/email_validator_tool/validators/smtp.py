import re

import aiosmtplib
import dns.resolver
from email_validator_tool.config import get_settings
from email_validator_tool.core.models import ValidationResult, ValidationStatus
from loguru import logger

from .throttle import enforce_domain_delay

# Throttling handled via validators.throttle module


class SMTPValidator:
    """Validator for checking email deliverability via SMTP with shared throttling"""

    def __init__(self):
        """Initialize the validator"""
        self.settings = get_settings()

    async def validate(self, email: str) -> ValidationResult:
        """
        Check if the email is deliverable via SMTP.

        Args:
            email: Email address to validate

        Returns:
            ValidationResult with the validation outcome
        """
        try:
            domain = email.split("@")[1]
            logger.debug(f"Checking SMTP deliverability for {email}")

            # Global throttle between validators
            await enforce_domain_delay(domain)

            # Get MX records
            try:
                mx_records = dns.resolver.resolve(domain, "MX")
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

            # Get the highest priority MX server
            # Remove trailing dot from FQDN to match certificate common names
            mx_host = str(mx_records[0].exchange).rstrip(".")
            logger.debug(f"Checking {email} via MX {mx_host}")

            try:
                async with aiosmtplib.SMTP(
                    hostname=mx_host, port=self.settings.SMTP_PORT, timeout=self.settings.SMTP_TIMEOUT
                ) as smtp:
                    # EHLO
                    await smtp.ehlo()

                    # MAIL FROM
                    mail_from = f"verify@{domain}"
                    await smtp.mail(mail_from)

                    # RCPT TO
                    response = await smtp.rcpt(email)

                    code = int(response.code)

                    # 2xx: Accepted
                    if 200 <= code < 300:
                        return ValidationResult(
                            email=email,
                            status=ValidationStatus.VALID,
                            details=f"SMTP verification successful via {mx_host}",
                        )

                    # 4xx: Temporary (greylisting, mailbox unavailable etc.)
                    if 400 <= code < 500:
                        return ValidationResult(
                            email=email,
                            status=ValidationStatus.TEMPORARY_ERROR,
                            details=f"Temporary SMTP error {code}: {_simplify_smtp_message(response.message)}",
                        )

                    # 5xx: Permanent failure – mailbox does not exist or other permanent issue
                    if 500 <= code < 600:
                        friendly = "Mailbox does not exist" if code == 550 else _simplify_smtp_message(response.message)
                        return ValidationResult(
                            email=email,
                            status=ValidationStatus.INVALID_SMTP,
                            details=f"Permanent SMTP error {code}: {friendly}",
                        )

                    # Fallback
                    return ValidationResult(
                        email=email,
                        status=ValidationStatus.UNKNOWN_ERROR,
                        details=f"Unexpected SMTP response code {code} from {mx_host}",
                    )

            except aiosmtplib.SMTPConnectError as e:
                logger.error(f"SMTP connection error for {email}: {str(e)}")
                return ValidationResult(
                    email=email,
                    status=ValidationStatus.UNKNOWN_ERROR,
                    details=f"SMTP connection error: {str(e)}",
                )
            except aiosmtplib.SMTPTimeoutError as e:
                logger.error(f"SMTP timeout for {email}: {str(e)}")
                return ValidationResult(
                    email=email,
                    status=ValidationStatus.UNKNOWN_ERROR,
                    details=f"SMTP timeout: {str(e)}",
                )
            except aiosmtplib.SMTPException as e:
                # Attempt to extract an SMTP code from the exception text to classify the error
                logger.error(f"SMTP error for {email}: {str(e)}")

                code = None
                try:
                    # str(e) might look like "(550, '5.1.1 ...', 'recipient')" – extract leading int
                    code = int(str(e).lstrip("( ").split(",")[0])
                except Exception:
                    pass

                if code is not None:
                    if 400 <= code < 500:
                        status = ValidationStatus.TEMPORARY_ERROR
                    elif 500 <= code < 600:
                        status = ValidationStatus.INVALID_SMTP
                    else:
                        status = ValidationStatus.UNKNOWN_ERROR
                else:
                    status = ValidationStatus.UNKNOWN_ERROR

                # Extract the human-readable part between single quotes if present
                human_msg_match = re.search(r"'([^']+)'", str(e))
                human_msg = human_msg_match.group(1) if human_msg_match else str(e)

                if code == 550:
                    simplified_msg = "SMTP error 550: Mailbox does not exist"
                else:
                    simplified_msg = _simplify_smtp_message(human_msg)
                    if code is not None:
                        simplified_msg = f"SMTP error {code}: {simplified_msg}"

                return ValidationResult(
                    email=email,
                    status=status,
                    details=simplified_msg,
                )

        except Exception as e:
            logger.error(f"Error during SMTP verification of {email}: {str(e)}")
            return ValidationResult(
                email=email,
                status=ValidationStatus.UNKNOWN_ERROR,
                details=f"Error: {str(e)}",
            )


def _simplify_smtp_message(raw_msg):
    """Return a compact single-line description suitable for end-users."""
    if raw_msg is None:
        return ""

    if isinstance(raw_msg, (bytes, bytearray)):
        try:
            raw_msg = raw_msg.decode()
        except Exception:
            raw_msg = str(raw_msg)

    # Normalize whitespace
    message = " ".join(str(raw_msg).split())

    # Lower-cased copy for pattern matching
    lower_msg = message.lower()

    # Friendly mappings for well-known phrases
    if "greylist" in lower_msg:
        return "Greylisted – try again later"
    if "does not exist" in lower_msg or "no such user" in lower_msg or "user unknown" in lower_msg:
        return "Mailbox does not exist"
    if "quota" in lower_msg and ("exceed" in lower_msg or "exceeded" in lower_msg or "full" in lower_msg):
        return "Mailbox full / quota exceeded"

    # Fallback: truncate overly long technical message
    if len(message) > 120:
        message = message[:117] + "..."

    return message
