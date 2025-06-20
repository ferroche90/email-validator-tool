import asyncio
from typing import AsyncGenerator, List
from loguru import logger
from email_validator_tool.config import get_settings
from email_validator_tool.core.models import ValidationResult, ValidationStatus
from email_validator_tool.validators.syntax import SyntaxValidator
from email_validator_tool.validators.dns_mx import DNSMXValidator
from email_validator_tool.validators.disposable import DisposableValidator
from email_validator_tool.validators.role_account import RoleAccountValidator
from email_validator_tool.validators.bounce_list import BounceListValidator
from email_validator_tool.validators.catch_all import CatchAllValidator
from email_validator_tool.validators.smtp import SMTPValidator

class ValidationPipeline:
    """Pipeline for email validation with multiple layers"""
    
    def __init__(self):
        """Initialize validators based on settings"""
        # Get settings from centralized configuration
        settings = get_settings()
        
        # Initialize DNS validator with cache configuration
        dns_validator = DNSMXValidator(
            cache_ttl_seconds=settings.DNS_CACHE_TTL_SECONDS if settings.ENABLE_DNS_CACHE else 0
        )
        
        # Initialize bounce list validator
        bounce_validator = BounceListValidator()
        
        self.validators = [
            SyntaxValidator(),
            dns_validator,
            DisposableValidator(),
            RoleAccountValidator(),
            bounce_validator,
        ]
        
        # Add optional validators based on settings
        if settings.ENABLE_CATCH_ALL:
            self.validators.append(CatchAllValidator())
        
        if settings.ENABLE_SMTP:
            self.validators.append(SMTPValidator())
        
        # Store validator references for management
        self.dns_validator = dns_validator
        self.bounce_validator = bounce_validator
    
    def clear_dns_cache(self) -> int:
        """
        Clear the DNS cache and return the number of entries removed
        
        Returns:
            Number of cache entries removed
        """
        return self.dns_validator.clear_cache()
    
    def get_dns_cache_stats(self) -> dict:
        """
        Get DNS cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        return self.dns_validator.get_cache_stats()
    
    def cleanup_expired_dns_cache(self) -> int:
        """
        Manually cleanup expired DNS cache entries
        
        Returns:
            Number of expired entries removed
        """
        return self.dns_validator._cleanup_expired_cache()
    
    def reload_bounce_list(self) -> int:
        """
        Reload the bounce list from the database
        
        Returns:
            Number of bounce emails loaded
        """
        return self.bounce_validator.reload_bounce_list()
    
    def get_bounce_list_stats(self) -> dict:
        """
        Get bounce list statistics
        
        Returns:
            Dictionary with bounce list statistics
        """
        return {
            "bounce_count": self.bounce_validator.get_bounce_count(),
            "loaded_in_memory": True
        }
    
    async def run_pipeline(self, emails: List[str]) -> AsyncGenerator[ValidationResult, None]:
        """
        Run the validation pipeline on a list of emails concurrently.
        
        Args:
            emails: List of email addresses to validate
            
        Yields:
            ValidationResult for each processed email as they complete
        """
        # Get settings for concurrency control
        settings = get_settings()
        sem = asyncio.Semaphore(settings.MAX_CONCURRENT_CONNECTIONS)
        
        async def process_with_semaphore(email: str) -> ValidationResult:
            """Process a single email with semaphore control for concurrency limiting"""
            async with sem:
                try:
                    # Add a small delay for throttling if needed
                    # await asyncio.sleep(0.05)
                    return await self._process_email(email)
                except Exception as e:
                    logger.error(f"Error processing email {email}: {str(e)}")
                    return ValidationResult(
                        email=email,
                        status=ValidationStatus.UNKNOWN_ERROR,
                        details={"error": str(e)}
                    )
        
        # Create tasks for all emails
        tasks = [asyncio.create_task(process_with_semaphore(email)) for email in emails]
        
        # Process tasks as they complete
        for future in asyncio.as_completed(tasks):
            try:
                result = await future
                yield result
            except Exception as e:
                logger.error(f"Error in concurrent task: {str(e)}")
                # Create a generic error result if the task failed
                yield ValidationResult(
                    email="unknown",
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
