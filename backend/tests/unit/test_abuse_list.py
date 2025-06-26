"""Tests for the AbuseListValidator."""

import pytest
from email_validator_tool.core.models import ValidationStatus
from email_validator_tool.validators.abuse_list import AbuseListValidator


@pytest.mark.asyncio
async def test_abuse_exact_match():
    """Email exactly in the abuse list should be flagged as ABUSE."""
    validator = AbuseListValidator()
    email = "abuse@example.com"  # Present in sample list
    result = await validator.validate(email)
    assert result.status == ValidationStatus.ABUSE


@pytest.mark.asyncio
async def test_abuse_non_match():
    """Regular email should not be marked as abuse."""
    validator = AbuseListValidator()
    result = await validator.validate("john.doe@example.com")
    assert result.status == ValidationStatus.VALID


@pytest.mark.asyncio
async def test_abuse_case_insensitive():
    """Abuse detection should be case insensitive."""
    validator = AbuseListValidator()
    email = "ABUSE@EXAMPLE.COM"  # Present in sample list but uppercase
    result = await validator.validate(email)
    assert result.status == ValidationStatus.ABUSE


@pytest.mark.asyncio
async def test_abuse_reload():
    """Test reloading the abuse list."""
    validator = AbuseListValidator()
    initial_count = validator.get_abuse_count()
    reloaded_count = validator.reload_abuse_list()
    assert reloaded_count == initial_count  # Should be the same in test environment
