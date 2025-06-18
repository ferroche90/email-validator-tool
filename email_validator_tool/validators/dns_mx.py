import dns.resolver
from email_validator import validate_email, EmailNotValidError
from loguru import logger
from email_validator_tool.models import ValidationResult, ValidationStatus

async def check(email: str) -> ValidationResult:
    try:
        # Extract domain from email
        domain = email.split('@')[1]
        
        # Query MX records
        mx_records = dns.resolver.resolve(domain, 'MX')
        
        if mx_records:
            return ValidationResult(
                email=email,
                status=ValidationStatus.VALID
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
    except Exception as exc:
        logger.error(f"DNS error for {email}: {exc}")
        return ValidationResult(
            email=email,
            status=ValidationStatus.UNKNOWN_ERROR,
            details=str(exc)
        )
