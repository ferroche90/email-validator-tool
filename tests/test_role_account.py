"""
Tests for the role account validator.
"""

import pytest

from email_validator_tool.core.models import ValidationStatus
from email_validator_tool.validators.role_account import RoleAccountValidator


@pytest.mark.asyncio
async def test_role_account_validator_initialization():
    """Test role account validator initialization."""
    validator = RoleAccountValidator()
    assert validator is not None


@pytest.mark.asyncio
async def test_role_account_validation(valid_email):
    """Test role account validation with a valid email."""
    validator = RoleAccountValidator()
    result = await validator.validate(valid_email)
    assert result.status == ValidationStatus.VALID


@pytest.mark.asyncio
async def test_role_account_validation_with_role_account(role_account_email):
    """Test role account validation with a role account email."""
    validator = RoleAccountValidator()
    result = await validator.validate(role_account_email)
    assert result.status == ValidationStatus.ROLE_ACCOUNT


@pytest.mark.asyncio
async def test_role_account_validation_with_common_role_accounts():
    """Test role account validation with common role account emails."""
    validator = RoleAccountValidator()
    role_accounts = [
        "admin@example.com",
        "support@example.com",
        "info@example.com",
        "sales@example.com",
        "contact@example.com",
    ]
    for email in role_accounts:
        result = await validator.validate(email)
        assert result.status == ValidationStatus.ROLE_ACCOUNT


@pytest.mark.asyncio
async def test_role_account_validation_with_invalid_email(invalid_email):
    """Test role account validation with an invalid email."""
    validator = RoleAccountValidator()
    result = await validator.validate(invalid_email)
    assert result.status == ValidationStatus.VALID  # Role account validator doesn't validate syntax
