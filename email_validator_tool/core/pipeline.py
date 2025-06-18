import asyncio
from loguru import logger
from email_validator_tool.config import Settings
from email_validator_tool.models import ValidationResult
from email_validator_tool.validators import (
    syntax,
    dns_mx,
    disposable,
    role_account,
    bounce_list,
    catch_all,
    smtp,
)

SETTINGS = Settings()

async def process_email(email: str) -> ValidationResult:
    """
    Process a single email through all enabled validation layers.
    
    Args:
        email: Email address to validate
        
    Returns:
        ValidationResult with the final validation status
    """
    # Run safe validations in order
    validators = [
        syntax,
        dns_mx,
        disposable,
        role_account,
        bounce_list,
    ]
    
    for validator in validators:
        result = await validator.check(email)
        if result.status != "valid":
            return result
    
    # Optional validations based on settings
    if SETTINGS.ENABLE_CATCH_ALL:
        result = await catch_all.check(email)
        if result.status != "valid":
            return result
    
    if SETTINGS.ENABLE_SMTP:
        result = await smtp.check(email)
        if result.status != "valid":
            return result
    
    return ValidationResult(
        email=email,
        status="valid"
    )

async def run_pipeline(email_list: list[str]):
    """
    Run the validation pipeline on a list of emails with controlled concurrency.
    
    Args:
        email_list: List of email addresses to validate
        
    Yields:
        ValidationResult for each processed email
    """
    sem = asyncio.Semaphore(SETTINGS.MAX_CONCURRENT_CONNECTIONS)
    
    async def sem_task(email: str) -> ValidationResult:
        async with sem:
            return await process_email(email)
    
    # Create tasks for all emails
    tasks = [sem_task(email) for email in email_list]
    
    # Process tasks as they complete
    for coro in asyncio.as_completed(tasks):
        try:
            result = await coro
            yield result
        except Exception as e:
            logger.error(f"Error processing email: {str(e)}")
            yield ValidationResult(
                email=email,
                status="unknown_error",
                details=str(e)
            )
