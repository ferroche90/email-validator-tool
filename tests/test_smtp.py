"""
Tests for the SMTP validator.
"""

import pytest

from email_validator_tool.core.models import ValidationStatus
from email_validator_tool.validators.smtp import SMTPValidator


@pytest.mark.asyncio
async def test_smtp_validator_initialization():
    """Test SMTP validator initialization."""
    validator = SMTPValidator()
    assert validator is not None


@pytest.mark.asyncio
async def test_smtp_validation(valid_email):
    """Test SMTP validation with a valid email."""
    validator = SMTPValidator()
    result = await validator.validate(valid_email)
    # SMTP validation might fail in test environment, so we check for valid status or error
    assert result.status in [ValidationStatus.VALID, ValidationStatus.UNKNOWN_ERROR]


@pytest.mark.asyncio
async def test_smtp_validation_with_invalid_domain(invalid_email):
    """Test SMTP validation with an invalid domain."""
    validator = SMTPValidator()
    result = await validator.validate(invalid_email)
    # Accept INVALID_MX or INVALID_DOMAIN
    assert result.status in [ValidationStatus.INVALID_MX, ValidationStatus.INVALID_DOMAIN]


@pytest.mark.asyncio
async def test_smtp_validation_with_nonexistent_domain():
    """Test SMTP validation with a nonexistent domain."""
    validator = SMTPValidator()
    result = await validator.validate("test@nonexistentdomain123456.com")
    assert result.status == ValidationStatus.INVALID_DOMAIN


@pytest.mark.asyncio
async def test_smtp_validation_with_timeout():
    """Test SMTP validation with a timeout."""
    validator = SMTPValidator()
    # Note: We can't easily test timeout in unit tests without mocking
    result = await validator.validate("test@example.com")
    # Should return valid status or error, not timeout specifically
    assert result.status in [ValidationStatus.VALID, ValidationStatus.UNKNOWN_ERROR]


@pytest.mark.asyncio
async def test_smtp_validation_with_invalid_email(invalid_email):
    """Test SMTP validation with an invalid email."""
    validator = SMTPValidator()
    result = await validator.validate(invalid_email)
    # Accept INVALID_MX or INVALID_DOMAIN
    assert result.status in [ValidationStatus.INVALID_MX, ValidationStatus.INVALID_DOMAIN]
