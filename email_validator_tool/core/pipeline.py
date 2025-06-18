import asyncio
from typing import AsyncGenerator, List
from loguru import logger
from email_validator_tool.config import Settings
from email_validator_tool.core.models import ValidationResult, ValidationStatus
from email_validator_tool.validators.syntax import SyntaxValidator
from email_validator_tool.validators.dns_mx import DNSMXValidator
from email_validator_tool.validators.disposable import DisposableValidator
from email_validator_tool.validators.role_account import RoleAccountValidator
from email_validator_tool.validators.bounce_list import BounceListValidator
from email_validator_tool.validators.catch_all import CatchAllValidator
from email_validator_tool.validators.smtp import SMTPValidator

SETTINGS = Settings()

class ValidationPipeline:
    """Pipeline for email validation with multiple layers"""
    
    def __init__(self):
        """Initialize validators"""
        self.validators = [
            SyntaxValidator(),
            DNSMXValidator(),
            DisposableValidator(),
            RoleAccountValidator(),
            BounceListValidator(),
            CatchAllValidator(),
            SMTPValidator()
        ]
    
    async def run_pipeline(self, emails: List[str]) -> AsyncGenerator[ValidationResult, None]:
        """
        Run the validation pipeline on a list of emails.
        
        Args:
            emails: List of email addresses to validate
            
        Yields:
            ValidationResult for each processed email
        """
        for email in emails:
            try:
                result = await self._process_email(email)
                yield result
            except Exception as e:
                logger.error(f"Error processing email {email}: {str(e)}")
                yield ValidationResult(
                    email=email,
                    status=ValidationStatus.UNKNOWN_ERROR,
                    details={"error": str(e)}
                )
    
    async def _process_email(self, email: str) -> ValidationResult:
        """
        Process a single email through all validation layers.
        
        Args:
            email: Email address to validate
            
        Returns:
            ValidationResult with the validation outcome
        """
        for validator in self.validators:
            try:
                result = await validator.validate(email)
                if result.status != ValidationStatus.VALID:
                    return result
            except Exception as e:
                logger.error(f"Error in {validator.__class__.__name__} for {email}: {str(e)}")
                return ValidationResult(
                    email=email,
                    status=ValidationStatus.UNKNOWN_ERROR,
                    details={"error": str(e)}
                )
        
        return ValidationResult(
            email=email,
            status=ValidationStatus.VALID
        )
