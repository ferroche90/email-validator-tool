from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel


class ValidationStatus(Enum):
    """Validation status codes"""

    VALID = "valid"
    INVALID_SYNTAX = "invalid_syntax"
    INVALID_DOMAIN = "invalid_domain"
    INVALID_MX = "invalid_mx"
    DISPOSABLE = "disposable"
    ROLE_ACCOUNT = "role_account"
    SPAMTRAP = "spamtrap"
    ABUSE = "abuse"
    SUPPRESSED = "suppressed"
    ON_BOUNCE_LIST = "on_bounce_list"
    CATCH_ALL = "catch_all"
    INVALID_SMTP = "invalid_smtp"
    TEMPORARY_ERROR = "temporary_error"
    UNKNOWN_ERROR = "unknown_error"


class ValidationResult(BaseModel):
    """Result of email validation"""

    email: str
    status: ValidationStatus
    details: Optional[str] = None
    suggestion: Optional[str] = None
    meta: Dict[str, Any] = {}

    def to_dict(self, include_domain_info: bool = True, domain_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Convert validation result to a dictionary format suitable for API responses.

        Args:
            include_domain_info: Whether to include domain-related fields
            domain_info: Optional domain information to include

        Returns:
            Dictionary representation of the validation result
        """
        local_part, domain = (self.email.split("@", 1) + [""])[:2] if "@" in self.email else (self.email, "")

        meta = self.meta or {}
        free_provider_flag = meta.get("free_provider", False)

        # Base result structure
        result = {
            # Core fields
            "address": self.email,
            "email": self.email,  # Backward compatibility
            "status": self.status.value if isinstance(self.status, ValidationStatus) else str(self.status),
            "sub_status": self.details or "valid_email",
            "free_email": free_provider_flag,
            "did_you_mean": self.suggestion,
            "account": local_part,
            "domain": domain,
            "processed_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            # Backward compatibility fields
            "details": self.details or "Email validation completed successfully",
            "suggestion": self.suggestion,
            "is_valid": self.status == ValidationStatus.VALID,
        }

        # Add domain information if requested
        if include_domain_info and domain_info:
            result.update(
                {
                    "domain_age_days": domain_info.get("domain_age_days", ""),
                    "active_in_days": domain_info.get("active_in_days", ""),
                    "smtp_provider": domain_info.get("smtp_provider", ""),
                    "mx_record": domain_info.get("mx_record", ""),
                    "mx_found": domain_info.get("mx_found", False),
                    "city": domain_info.get("city", ""),
                    "region": domain_info.get("region", ""),
                    "zipcode": domain_info.get("zipcode", ""),
                    "country": domain_info.get("country", ""),
                }
            )

        # Enhanced meta with timestamp
        enhanced_meta = {
            **meta,
            "validation_timestamp": datetime.utcnow().isoformat(),
        }

        if include_domain_info and domain_info:
            enhanced_meta.update(
                {
                    "domain_age_days": domain_info.get("domain_age_days", "") if domain else "",
                    "mx_found": domain_info.get("mx_found", False) if domain else False,
                    "smtp_provider": domain_info.get("smtp_provider", "") if domain else "",
                }
            )

        result["meta"] = enhanced_meta

        return result

    @classmethod
    def create_error_result(cls, email: str, error_message: str) -> "ValidationResult":
        """
        Create a validation result for an error case.

        Args:
            email: The email that failed validation
            error_message: Description of the error

        Returns:
            ValidationResult with UNKNOWN_ERROR status
        """
        return cls(email=email, status=ValidationStatus.UNKNOWN_ERROR, details=error_message, meta={})
