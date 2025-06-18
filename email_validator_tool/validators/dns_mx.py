import dns.resolver
from email_validator import validate_email, EmailNotValidError
from loguru import logger
from email_validator_tool.core.models import ValidationResult, ValidationStatus

class DNSMXValidator:
    """Validator for DNS MX records"""
    
    async def validate(self, email: str) -> ValidationResult:
        try:
            # Extract domain from email
            domain = email.split('@')[1]
            logger.debug(f"Checking MX records for domain: {domain}")
            
            # Query MX records
            mx_records = dns.resolver.resolve(domain, 'MX')
            
            if mx_records:
                logger.info(f"Found {len(mx_records)} MX records for {domain}")
                return ValidationResult(
                    email=email,
                    status=ValidationStatus.VALID
                )
                
        except dns.resolver.NXDOMAIN:
            logger.warning(f"Domain {domain} does not exist")
            return ValidationResult(
                email=email,
                status=ValidationStatus.INVALID_DOMAIN,
                details=f"Domain {domain} does not exist"
            )
        except dns.resolver.NoAnswer:
            logger.warning(f"No MX records found for domain {domain}")
            return ValidationResult(
                email=email,
                status=ValidationStatus.INVALID_MX,
                details=f"No MX records found for domain {domain}"
            )
        except Exception as exc:
            logger.error(f"DNS error for {email}: {exc}")
            return ValidationResult(
                email=email,
                status=ValidationStatus.UNKNOWN_ERROR,
                details=f"DNS error: {str(exc)}"
            )

async def check(email: str) -> ValidationResult:
    """Convenience wrapper to validate a single email."""
    return await DNSMXValidator().validate(email)

