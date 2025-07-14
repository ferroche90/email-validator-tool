from typing import List, Optional

from email_validator_tool.core.domain_info import get_domain_info
from email_validator_tool.core.pipeline import ValidationPipeline
from email_validator_tool.core.results import convert_results_to_dicts
from email_validator_tool.validators.bounce_list import BounceListValidator
from email_validator_tool.validators.dns_mx import DNSMXValidator


class EmailValidatorService:
    """
    Service adapter for email validation using the core ValidationPipeline.
    Uses pre-created global validator instances for better performance and resource sharing.
    """

    def __init__(
        self,
        dns_validator: Optional[DNSMXValidator] = None,
        bounce_validator: Optional[BounceListValidator] = None,
    ):
        """
        Initialize service with optional validator instances.
        If not provided, will create new instances (fallback for testing).

        Args:
            dns_validator: Pre-created DNS validator instance for sharing cache
            bounce_validator: Pre-created bounce list validator for sharing data
        """
        self.dns_validator = dns_validator
        self.bounce_validator = bounce_validator

    async def validate_many(
        self,
        emails: List[str],
        enable_smtp: bool = False,
        enable_catch_all: bool = False,
    ) -> List[dict]:
        """
        Validate a list of emails using the ValidationPipeline with dependency injection.
        Returns a list of dicts (one per email), serializing enums as strings.
        Any exception is caught and returned as UNKNOWN_ERROR for that email.
        """
        try:
            # Create pipeline with injected validators and configuration flags
            pipeline = ValidationPipeline(
                dns_validator=self.dns_validator,
                bounce_validator=self.bounce_validator,
                enable_smtp=enable_smtp,
                enable_catch_all=enable_catch_all,
            )

            # Collect validation results
            validation_results = []
            async for result in pipeline.run_pipeline(emails):
                validation_results.append(result)

            # Build domain info map for enrichment
            domain_info_map = {}
            for result in validation_results:
                if "@" in result.email:
                    domain = result.email.split("@")[-1]
                    if domain not in domain_info_map:
                        domain_info_map[domain] = get_domain_info(domain)

            # Use core functionality to convert results to dictionaries
            return convert_results_to_dicts(validation_results, domain_info_map)

        except Exception as e:
            # If something fails globally, return UNKNOWN_ERROR for all
            from email_validator_tool.core.models import ValidationResult

            error_results = [
                ValidationResult.create_error_result(email, f"Service error: {str(e)}") for email in emails
            ]
            return convert_results_to_dicts(error_results)
