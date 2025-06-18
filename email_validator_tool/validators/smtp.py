import asyncio
import time
from typing import Dict
import dns.resolver
import aiosmtplib
from email.mime.text import MIMEText
from loguru import logger
from email_validator_tool.core.models import ValidationResult, ValidationStatus
from email_validator_tool.config import Settings

SETTINGS = Settings()

# Keep track of last contact time per domain
_last_contact: Dict[str, float] = {}

class SMTPValidator:
    """Validator for checking email deliverability via SMTP"""
    
    def __init__(self):
        """Initialize the validator"""
        self.settings = Settings()
    
    async def validate(self, email: str) -> ValidationResult:
        """
        Check if the email is deliverable via SMTP.
        
        Args:
            email: Email address to validate
            
        Returns:
            ValidationResult with the validation outcome
        """
        try:
            domain = email.split('@')[1]
            logger.debug(f"Checking SMTP deliverability for {email}")
            
            # Create test message
            msg = MIMEText("This is a test message for email validation.")
            msg['Subject'] = "Email Validation Test"
            msg['From'] = "validator@example.com"
            msg['To'] = email
            
            # Try to connect to SMTP server
            try:
                async with aiosmtplib.SMTP(
                    hostname=domain,
                    port=self.settings.SMTP_PORT,
                    timeout=self.settings.SMTP_TIMEOUT
                ) as smtp:
                    # Send test message
                    await smtp.send_message(msg)
                    logger.info(f"Email {email} is deliverable via SMTP")
                    return ValidationResult(
                        email=email,
                        status=ValidationStatus.VALID
                    )
            except Exception as e:
                logger.warning(f"Email {email} is not deliverable via SMTP: {str(e)}")
                return ValidationResult(
                    email=email,
                    status=ValidationStatus.INVALID_SMTP,
                    details={"reason": f"SMTP error: {str(e)}"}
                )
                
        except Exception as e:
            logger.error(f"Error validating SMTP deliverability for {email}: {str(e)}")
            return ValidationResult(
                email=email,
                status=ValidationStatus.UNKNOWN_ERROR,
                details={"error": str(e)}
            )

async def check(email: str) -> ValidationResult:
    """
    Perform SMTP verification of an email address.
    
    Args:
        email: Email address to verify
        
    Returns:
        ValidationResult with the verification status
    """
    try:
        # Extract domain from email
        domain = email.split('@')[1]
        
        # Check and enforce delay between requests to the same domain
        current_time = time.time()
        if domain in _last_contact:
            time_since_last = current_time - _last_contact[domain]
            if time_since_last < SETTINGS.PER_DOMAIN_DELAY_SECONDS:
                delay = SETTINGS.PER_DOMAIN_DELAY_SECONDS - time_since_last
                logger.debug(f"Waiting {delay:.1f}s before checking {domain}")
                await asyncio.sleep(delay)
        
        # Update last contact time
        _last_contact[domain] = time.time()
        
        # Get MX records
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            if not mx_records:
                return ValidationResult(
                    email=email,
                    status=ValidationStatus.INVALID_MX,
                    details="No MX records found"
                )
        except dns.resolver.NXDOMAIN:
            return ValidationResult(
                email=email,
                status=ValidationStatus.INVALID_DOMAIN,
                details="Domain does not exist"
            )
        except dns.resolver.NoAnswer:
            return ValidationResult(
                email=email,
                status=ValidationStatus.INVALID_MX,
                details="No MX records found"
            )
        
        # Get the highest priority MX server
        mx_host = str(mx_records[0].exchange)
        logger.debug(f"Checking {email} via MX {mx_host}")
        
        try:
            async with aiosmtplib.SMTP(
                hostname=mx_host,
                port=25,
                timeout=SETTINGS.SMTP_TIMEOUT
            ) as smtp:
                # EHLO
                await smtp.ehlo()
                
                # MAIL FROM
                mail_from = f"verify@{domain}"
                await smtp.mail(mail_from)
                
                # RCPT TO
                response = await smtp.rcpt(email)
                
                if response.code == 250:
                    return ValidationResult(
                        email=email,
                        status=ValidationStatus.VALID,
                        details=f"SMTP verification successful via {mx_host}"
                    )
                elif response.code == 550:
                    return ValidationResult(
                        email=email,
                        status=ValidationStatus.INVALID_SMTP,
                        details=f"Mailbox does not exist (response from {mx_host})"
                    )
                else:
                    return ValidationResult(
                        email=email,
                        status=ValidationStatus.UNKNOWN_ERROR,
                        details=f"Unexpected SMTP response code {response.code} from {mx_host}"
                    )
                    
        except aiosmtplib.SMTPConnectError as e:
            logger.error(f"SMTP connection error for {email}: {str(e)}")
            return ValidationResult(
                email=email,
                status=ValidationStatus.UNKNOWN_ERROR,
                details=f"SMTP connection error: {str(e)}"
            )
        except aiosmtplib.SMTPTimeoutError as e:
            logger.error(f"SMTP timeout for {email}: {str(e)}")
            return ValidationResult(
                email=email,
                status=ValidationStatus.UNKNOWN_ERROR,
                details=f"SMTP timeout: {str(e)}"
            )
        except aiosmtplib.SMTPException as e:
            logger.error(f"SMTP error for {email}: {str(e)}")
            return ValidationResult(
                email=email,
                status=ValidationStatus.UNKNOWN_ERROR,
                details=f"SMTP error: {str(e)}"
            )
            
    except Exception as e:
        logger.error(f"Error during SMTP verification of {email}: {str(e)}")
        return ValidationResult(
            email=email,
            status=ValidationStatus.UNKNOWN_ERROR,
            details=f"Error: {str(e)}"
        )
