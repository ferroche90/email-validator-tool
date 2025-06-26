from typing import Dict, List

from email_validator_tool.core.models import ValidationResult, ValidationStatus
from loguru import logger


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
    status_counts: Dict[ValidationStatus, int] = {}
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
    invalid_emails = [r for r in results if r.status != ValidationStatus.VALID]
    if invalid_emails:
        logger.info("\nInvalid Emails Details:")
        logger.info("-" * 50)
        for result in invalid_emails:
            logger.info(f"\nEmail: {result.email}")
            logger.info(f"Status: {result.status}")
            if result.details:
                logger.info(f"Details: {result.details}")
