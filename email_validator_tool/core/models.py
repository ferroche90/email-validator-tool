from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ValidationStatus(Enum):
    """Validation status codes"""

    VALID = "valid"
    INVALID_SYNTAX = "invalid_syntax"
    INVALID_DOMAIN = "invalid_domain"
    INVALID_MX = "invalid_mx"
    DISPOSABLE = "disposable"
    ROLE_ACCOUNT = "role_account"
    ON_BOUNCE_LIST = "on_bounce_list"
    CATCH_ALL = "catch_all"
    INVALID_SMTP = "invalid_smtp"
    UNKNOWN_ERROR = "unknown_error"


class ValidationResult(BaseModel):
    """Result of email validation"""

    email: str
    status: ValidationStatus
    details: Optional[str] = None
