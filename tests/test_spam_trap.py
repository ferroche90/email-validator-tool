"""Tests for the SpamTrapValidator."""

import pytest

from email_validator_tool.core.models import ValidationStatus
from email_validator_tool.validators.spam_trap import SpamTrapValidator


# Use pytest-asyncio for async validator


@pytest.mark.asyncio
async def test_spamtrap_exact_match():
    """Email exactly in the spam-trap list should be flagged as SPAMTRAP."""
    validator = SpamTrapValidator()
    email = "spamtrap@example.com"  # Present in sample list
    result = await validator.validate(email)
    assert result.status == ValidationStatus.SPAMTRAP


@pytest.mark.asyncio
async def test_spamtrap_heuristic():
    """Email matching heuristic pattern should be flagged as SPAMTRAP."""
    validator = SpamTrapValidator()
    email = "spam@heuristic.com"
    result = await validator.validate(email)
    assert result.status == ValidationStatus.SPAMTRAP


@pytest.mark.asyncio
async def test_spamtrap_non_match():
    """Regular email should not be marked as spam-trap."""
    validator = SpamTrapValidator()
    result = await validator.validate("john.doe@example.com")
    assert result.status == ValidationStatus.VALID 