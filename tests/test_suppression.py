"""Tests for the SuppressionValidator."""

import pytest

from email_validator_tool.core.models import ValidationStatus
from email_validator_tool.validators.suppression import SuppressionValidator


@pytest.mark.asyncio
async def test_suppression_initialization():
    """Test suppression validator initialization."""
    validator = SuppressionValidator()
    assert validator is not None
    assert validator.get_suppression_count() >= 0


@pytest.mark.asyncio
async def test_suppression_add_and_validate():
    """Test adding suppressions and validating them."""
    validator = SuppressionValidator()

    # Add a test suppression
    test_email = "test@suppression.com"
    added_count = validator.add_suppressions({test_email})
    assert added_count == 1

    # Validate the suppressed email
    result = await validator.validate(test_email)
    assert result.status == ValidationStatus.SUPPRESSED

    # Validate a non-suppressed email
    result = await validator.validate("john.doe@example.com")
    assert result.status == ValidationStatus.VALID


@pytest.mark.asyncio
async def test_suppression_case_insensitive():
    """Suppression detection should be case insensitive."""
    validator = SuppressionValidator()

    # Add suppression in lowercase
    test_email = "test@case.com"
    validator.add_suppressions({test_email})

    # Test with different cases
    result = await validator.validate("TEST@CASE.COM")
    assert result.status == ValidationStatus.SUPPRESSED

    result = await validator.validate("Test@Case.com")
    assert result.status == ValidationStatus.SUPPRESSED


@pytest.mark.asyncio
async def test_suppression_duplicate_add():
    """Adding the same email twice should not create duplicates."""
    validator = SuppressionValidator()

    test_email = "duplicate@test.com"

    # Add first time
    added_count1 = validator.add_suppressions({test_email})
    assert added_count1 == 1

    # Add second time (should be ignored)
    added_count2 = validator.add_suppressions({test_email})
    assert added_count2 == 0

    # Should still be suppressed
    result = await validator.validate(test_email)
    assert result.status == ValidationStatus.SUPPRESSED


@pytest.mark.asyncio
async def test_suppression_reload():
    """Test reloading the suppression list."""
    validator = SuppressionValidator()
    initial_count = validator.get_suppression_count()
    reloaded_count = validator.reload_suppression_list()
    assert reloaded_count == initial_count  # Should be the same after reload
