import random
import string
import aiosmtplib
from email.mime.text import MIMEText
from loguru import logger
from email_validator_tool.models import ValidationResult, ValidationStatus
from email_validator_tool.config import Settings

SETTINGS = Settings()

def generate_random_email(domain: str) -> str:
    """Generate a random email address for the given domain."""
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
    return f"{random_string}@{domain}"

async def check(email: str) -> ValidationResult:
    """
    Check if the email's domain is catch-all by testing a random email address.
    
    Args:
        email: Email address to check
        
    Returns:
        ValidationResult indicating if the domain is catch-all
    """
    try:
        # Extract domain from email
        domain = email.split('@')[1]
        
        # Generate random test email
        test_email = generate_random_email(domain)
        logger.debug(f"Testing catch-all with random email: {test_email}")
        
        # Create test message
        message = MIMEText("Test message for catch-all detection")
        message["From"] = "test@example.com"
        message["To"] = test_email
        
        # Get MX records for the domain
        mx_records = await aiosmtplib.get_mx_records(domain)
        if not mx_records:
            return ValidationResult(
                email=email,
                status=ValidationStatus.INVALID_MX,
                details="No MX records found for catch-all test"
            )
        
        # Try to send to the first MX server
        mx_host = mx_records[0].host
        try:
            async with aiosmtplib.SMTP(
                hostname=mx_host,
                port=25,
                timeout=SETTINGS.SMTP_TIMEOUT
            ) as smtp:
                # Send test message
                response = await smtp.send_message(message)
                
                # Check response code
                if response.code == 250:
                    return ValidationResult(
                        email=email,
                        status=ValidationStatus.CATCH_ALL,
                        details=f"Domain {domain} is catch-all (accepted random email)"
                    )
                elif response.code == 550:
                    return ValidationResult(
                        email=email,
                        status=ValidationStatus.VALID,
                        details=f"Domain {domain} is not catch-all (rejected random email)"
                    )
                else:
                    return ValidationResult(
                        email=email,
                        status=ValidationStatus.UNKNOWN_ERROR,
                        details=f"Unexpected SMTP response code: {response.code}"
                    )
                    
        except aiosmtplib.SMTPException as e:
            logger.error(f"SMTP error during catch-all check for {domain}: {str(e)}")
            return ValidationResult(
                email=email,
                status=ValidationStatus.UNKNOWN_ERROR,
                details=f"SMTP error: {str(e)}"
            )
            
    except Exception as e:
        logger.error(f"Error during catch-all check for {email}: {str(e)}")
        return ValidationResult(
            email=email,
            status=ValidationStatus.UNKNOWN_ERROR,
            details=f"Error: {str(e)}"
        )
