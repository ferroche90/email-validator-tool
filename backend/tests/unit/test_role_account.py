"""
Tests for the role account validator.
"""

import pytest
from email_validator_tool.constants import COMMON_ROLE_ACCOUNTS
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
async def test_role_account_validation_uses_constants():
    """Test that the validator uses the COMMON_ROLE_ACCOUNTS constant."""
    validator = RoleAccountValidator()

    # Test a few role accounts from the constant
    for role_account in ["admin", "info", "support", "sales", "contact"]:
        email = f"{role_account}@example.com"
        result = await validator.validate(email)
        assert result.status == ValidationStatus.ROLE_ACCOUNT
        assert role_account in COMMON_ROLE_ACCOUNTS

    # Test a non-role account
    result = await validator.validate("john.doe@example.com")
    assert result.status == ValidationStatus.VALID
    assert "john.doe" not in COMMON_ROLE_ACCOUNTS
