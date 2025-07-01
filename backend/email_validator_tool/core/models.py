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
