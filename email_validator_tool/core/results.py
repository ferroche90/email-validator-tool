from typing import List, Dict
from loguru import logger
from email_validator_tool.core.models import ValidationResult

def generate_summary(results: List[ValidationResult]) -> None:
    """
    Generate and display a summary of validation results.
    
    Args:
        results: List of validation results
    """
    if not results:
        logger.warning("No results to summarize")
        return
        
    # Count results by status
    status_counts: Dict[str, int] = {}
    for result in results:
        status = result.status
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Display summary
    logger.info("\nValidation Summary:")
    logger.info("-" * 50)
    logger.info(f"Total emails processed: {len(results)}")
    
    for status, count in status_counts.items():
        percentage = (count / len(results)) * 100
        logger.info(f"{status}: {count} ({percentage:.1f}%)")
    
    # Display details for invalid emails
    invalid_emails = [r for r in results if r.status != "valid"]
    if invalid_emails:
        logger.info("\nInvalid Emails Details:")
        logger.info("-" * 50)
        for result in invalid_emails:
            logger.info(f"\nEmail: {result.email}")
            logger.info(f"Status: {result.status}")
            if result.details:
                logger.info("Details:")
                for key, value in result.details.items():
                    logger.info(f"  - {key}: {value}")
