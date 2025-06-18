from disposable_email_domains import blocklist
from email_validator_tool.models import ValidationResult, ValidationStatus

async def check(email: str) -> ValidationResult:
    # Extract domain from email
    domain = email.split('@')[1]
    
    if domain in blocklist:
        return ValidationResult(
            email=email,
            status=ValidationStatus.DISPOSABLE,
            details=f"Domain {domain} is in disposable email list"
        )
    
    return ValidationResult(
        email=email,
        status=ValidationStatus.VALID
    )
