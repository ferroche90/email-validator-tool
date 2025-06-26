from typing import List, Optional

from email_validator_tool.core.models import ValidationStatus
from email_validator_tool.core.pipeline import ValidationPipeline
from email_validator_tool.validators.bounce_list import BounceListValidator
from email_validator_tool.validators.dns_mx import DNSMXValidator
from email_validator_tool.validators.spam_trap import SpamTrapValidator
from email_validator_tool.validators.abuse_list import AbuseListValidator
from email_validator_tool.validators.suppression import SuppressionValidator


class EmailValidatorService:
    """
    Service adapter for email validation using the core ValidationPipeline.
    Uses pre-created global validator instances for better performance and resource sharing.
    """

    def __init__(
        self,
        dns_validator: Optional[DNSMXValidator] = None,
        bounce_validator: Optional[BounceListValidator] = None,
        spamtrap_validator: Optional["SpamTrapValidator"] = None,
        abuse_validator: Optional["AbuseListValidator"] = None,
        suppression_validator: Optional["SuppressionValidator"] = None,
    ):
        """
        Initialize service with optional validator instances.
        If not provided, will create new instances (fallback for testing).

        Args:
            dns_validator: Pre-created DNS validator instance for sharing cache
            bounce_validator: Pre-created bounce list validator for sharing data
            spamtrap_validator: Pre-created spamtrap validator for sharing data
            abuse_validator: Pre-created abuse list validator for sharing data
            suppression_validator: Pre-created suppression validator for sharing data
        """
        self.dns_validator = dns_validator
        self.bounce_validator = bounce_validator
        self.spamtrap_validator = spamtrap_validator
        self.abuse_validator = abuse_validator
        self.suppression_validator = suppression_validator

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
        results = []
        try:
            # Create pipeline with injected validators and configuration flags
            pipeline = ValidationPipeline(
                dns_validator=self.dns_validator,
                bounce_validator=self.bounce_validator,
                spamtrap_validator=self.spamtrap_validator,
                abuse_validator=self.abuse_validator,
                suppression_validator=self.suppression_validator,
                enable_smtp=enable_smtp,
                enable_catch_all=enable_catch_all,
            )

            async for result in pipeline.run_pipeline(emails):
                # Convert ValidationResult to dict, enum as string
                results.append(
                    {
                        **result.model_dump(),
                        "status": (
                            result.status.value if isinstance(result.status, ValidationStatus) else str(result.status)
                        ),
                    }
                )
        except Exception as e:
            # If something fails globally, return UNKNOWN_ERROR for all
            for email in emails:
                results.append(
                    {
                        "email": email,
                        "status": ValidationStatus.UNKNOWN_ERROR.value,
                        "details": f"Service error: {str(e)}",
                    }
                )
        return results
