"""
Tests for the catch-all validator.
"""

import pytest
from email_validator_tool.core.models import ValidationStatus
from email_validator_tool.validators.catch_all import CatchAllValidator


@pytest.mark.asyncio
async def test_catch_all_validator_initialization():
    """Test catch-all validator initialization."""
    validator = CatchAllValidator()
    assert validator is not None


@pytest.mark.asyncio
async def test_catch_all_validation(valid_email):
    """Test catch-all validation with a valid email."""
    validator = CatchAllValidator()
    result = await validator.validate(valid_email)
    assert result.status in [ValidationStatus.VALID, ValidationStatus.UNKNOWN_ERROR]


@pytest.mark.asyncio
async def test_catch_all_validation_with_invalid_domain(invalid_email):
    """Test catch-all validation with an invalid domain."""
    validator = CatchAllValidator()
    result = await validator.validate(invalid_email)
    assert result.status in [
        ValidationStatus.INVALID_MX,
        ValidationStatus.INVALID_DOMAIN,
        ValidationStatus.INVALID_SYNTAX,
    ]


@pytest.mark.asyncio
async def test_catch_all_validation_with_nonexistent_domain():
    """Test catch-all validation with a nonexistent domain."""
    validator = CatchAllValidator()
    result = await validator.validate("test@nonexistentdomain123456.com")
    assert result.status in [ValidationStatus.INVALID_DOMAIN, ValidationStatus.INVALID_MX]
