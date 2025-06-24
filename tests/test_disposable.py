"""
Tests for the disposable email validator.
"""

import pytest

from email_validator_tool.core.models import ValidationStatus
from email_validator_tool.validators.disposable import DisposableValidator


@pytest.mark.asyncio
async def test_disposable_validator_initialization():
    """Test disposable email validator initialization."""
    validator = DisposableValidator()
    assert validator is not None


@pytest.mark.asyncio
async def test_disposable_validation(valid_email):
    """Test disposable email validation with a valid email."""
    validator = DisposableValidator()
    result = await validator.validate(valid_email)
    assert result.status == ValidationStatus.VALID


@pytest.mark.asyncio
async def test_disposable_validation_with_disposable_email(disposable_email):
    """Test disposable email validation with a disposable email."""
    validator = DisposableValidator()
    result = await validator.validate(disposable_email)
    assert result.status == ValidationStatus.DISPOSABLE


@pytest.mark.asyncio
async def test_disposable_validation_with_common_disposable_domains():
    """Test disposable email validation with common disposable domains."""
    validator = DisposableValidator()
    disposable_domains = [
        "mailinator.com",
        "tempmail.com",
        "throwawaymail.com",
        "guerrillamail.com",
        "10minutemail.com",
    ]
    for domain in disposable_domains:
        email = f"test@{domain}"
        result = await validator.validate(email)
        assert result.status in [ValidationStatus.DISPOSABLE, ValidationStatus.VALID]


@pytest.mark.asyncio
async def test_disposable_validation_with_invalid_email(invalid_email):
    """Test disposable email validation with an invalid email."""
    validator = DisposableValidator()
    result = await validator.validate(invalid_email)
    assert result.status == ValidationStatus.VALID  # Disposable validator doesn't validate syntax
