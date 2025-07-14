from datetime import datetime
from typing import List, Optional

from email_validator_tool.core.models import ValidationStatus
from email_validator_tool.core.pipeline import ValidationPipeline
from email_validator_tool.validators.bounce_list import BounceListValidator
from email_validator_tool.validators.dns_mx import DNSMXValidator

from .domain_info import get_domain_info


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
        results = []
        try:
            # Create pipeline with injected validators and configuration flags
            pipeline = ValidationPipeline(
                dns_validator=self.dns_validator,
                bounce_validator=self.bounce_validator,
                enable_smtp=enable_smtp,
                enable_catch_all=enable_catch_all,
            )

            async for result in pipeline.run_pipeline(emails):
                # Build ZeroBounce-style response object per e-mail
                local_part, domain = (
                    (result.email.split("@", 1) + [""])[:2] if "@" in result.email else (result.email, "")
                )
                meta = result.meta or {}
                free_provider_flag = meta.get("free_provider", False)

                # Enrich with domain information (MX, age, provider)
                domain_info = (
                    get_domain_info(domain)
                    if domain
                    else {
                        "domain_age_days": "",
                        "mx_record": "",
                        "mx_found": False,
                        "smtp_provider": "",
                    }
                )

                # Enhance meta with additional information
                enhanced_meta = {
                    **meta,
                    "validation_timestamp": datetime.utcnow().isoformat(),
                    "domain_age_days": domain_info["domain_age_days"] if domain else "",
                    "mx_found": domain_info["mx_found"] if domain else False,
                    "smtp_provider": domain_info["smtp_provider"] if domain else "",
                }

                results.append(
                    {
                        # Core fields
                        "address": result.email,
                        "email": result.email,  # Backward compatibility for frontend
                        "status": (
                            result.status.value if isinstance(result.status, ValidationStatus) else str(result.status)
                        ),
                        "sub_status": result.details or "valid_email",
                        "free_email": free_provider_flag,
                        "did_you_mean": result.suggestion,
                        "account": local_part,
                        "domain": domain,
                        "domain_age_days": domain_info["domain_age_days"],
                        "active_in_days": domain_info["active_in_days"],
                        "smtp_provider": domain_info["smtp_provider"],
                        "mx_record": domain_info["mx_record"],
                        "mx_found": domain_info["mx_found"],
                        "city": domain_info["city"],
                        "region": domain_info["region"],
                        "zipcode": domain_info["zipcode"],
                        "country": domain_info["country"],
                        "processed_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                        # Keep original fields for backward-compatibility
                        "details": result.details or "Email validation completed successfully",
                        "suggestion": result.suggestion,
                        "meta": enhanced_meta,
                        "is_valid": result.status == ValidationStatus.VALID,
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
