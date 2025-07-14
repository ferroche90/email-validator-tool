from typing import Any, Dict, List, Optional

from email_validator_tool.core.models import ValidationResult, ValidationStatus
from loguru import logger


def convert_results_to_dicts(
    results: List[ValidationResult], domain_info_map: Optional[Dict[str, Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Convert a list of ValidationResult objects to dictionaries suitable for API responses.

    Args:
        results: List of validation results
        domain_info_map: Optional mapping of domain -> domain_info for enrichment

    Returns:
        List of dictionaries representing validation results
    """
    domain_info_map = domain_info_map or {}

    return [
        result.to_dict(
            include_domain_info=True,
            domain_info=domain_info_map.get(result.email.split("@")[-1] if "@" in result.email else ""),
        )
        for result in results
    ]


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
