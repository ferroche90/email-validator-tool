"""
Tests for the role account validator.
"""

import pytest
from email_validator_tool.validators.role_account import RoleAccountValidator

def test_role_account_validator_initialization():
    """Test role account validator initialization."""
    validator = RoleAccountValidator()
    assert validator is not None
    assert validator.name == "role_account"

def test_role_account_validation(valid_email, validation_result):
    """Test role account validation with a valid email."""
    validator = RoleAccountValidator()
    result = validator.validate(valid_email, validation_result)
    assert isinstance(result, bool)
    assert result is True

def test_role_account_validation_with_role_account(role_account_email, validation_result):
    """Test role account validation with a role account email."""
    validator = RoleAccountValidator()
    result = validator.validate(role_account_email, validation_result)
    assert isinstance(result, bool)
    assert result is False

def test_role_account_validation_with_common_role_accounts(validation_result):
    """Test role account validation with common role account emails."""
    validator = RoleAccountValidator()
    role_accounts = [
        "admin@example.com",
        "support@example.com",
        "info@example.com",
        "sales@example.com",
        "contact@example.com"
    ]
    for email in role_accounts:
        result = validator.validate(email, validation_result)
        assert isinstance(result, bool)
        assert result is False

def test_role_account_validation_with_invalid_email(invalid_email, validation_result):
    """Test role account validation with an invalid email."""
    validator = RoleAccountValidator()
    result = validator.validate(invalid_email, validation_result)
    assert isinstance(result, bool)
    assert result is False
