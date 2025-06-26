"""
Tests for the bounce list validator.
"""

import pytest
from email_validator_tool.core.models import ValidationStatus
from email_validator_tool.validators.bounce_list import BounceListValidator


@pytest.mark.asyncio
async def test_bounce_list_validator_initialization():
    """Test bounce list validator initialization."""
    validator = BounceListValidator()
    assert validator is not None


@pytest.mark.asyncio
async def test_bounce_list_validation(valid_email):
    """Test bounce list validation with a valid email."""
    validator = BounceListValidator()
    result = await validator.validate(valid_email)
    assert result.status == ValidationStatus.VALID


@pytest.mark.asyncio
async def test_bounce_list_validation_with_bounced_email():
    """Test bounce list validation with a bounced email."""
    validator = BounceListValidator()
    # Add a test bounced email to the list
    validator.bounce_set.add("bounced@example.com")
    result = await validator.validate("bounced@example.com")
    assert result.status == ValidationStatus.ON_BOUNCE_LIST


@pytest.mark.asyncio
async def test_bounce_list_validation_with_invalid_email(invalid_email):
    """Test bounce list validation with an invalid email."""
    validator = BounceListValidator()
    result = await validator.validate(invalid_email)
    assert result.status == ValidationStatus.VALID  # Bounce list doesn't validate syntax
