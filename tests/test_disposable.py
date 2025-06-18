"""
Tests for the disposable email validator.
"""

import pytest
from email_validator_tool.validators.disposable import DisposableEmailValidator

def test_disposable_validator_initialization():
    """Test disposable email validator initialization."""
    validator = DisposableEmailValidator()
    assert validator is not None
    assert validator.name == "disposable"

def test_disposable_validation(valid_email, validation_result):
    """Test disposable email validation with a valid email."""
    validator = DisposableEmailValidator()
    result = validator.validate(valid_email, validation_result)
    assert isinstance(result, bool)
    assert result is True

def test_disposable_validation_with_disposable_email(disposable_email, validation_result):
    """Test disposable email validation with a disposable email."""
    validator = DisposableEmailValidator()
    result = validator.validate(disposable_email, validation_result)
    assert isinstance(result, bool)
    assert result is False

def test_disposable_validation_with_common_disposable_domains(validation_result):
    """Test disposable email validation with common disposable domains."""
    validator = DisposableEmailValidator()
    disposable_domains = [
        "mailinator.com",
        "tempmail.com",
        "throwawaymail.com",
        "guerrillamail.com",
        "10minutemail.com"
    ]
    for domain in disposable_domains:
        email = f"test@{domain}"
        result = validator.validate(email, validation_result)
        assert isinstance(result, bool)
        assert result is False

def test_disposable_validation_with_invalid_email(invalid_email, validation_result):
    """Test disposable email validation with an invalid email."""
    validator = DisposableEmailValidator()
    result = validator.validate(invalid_email, validation_result)
    assert isinstance(result, bool)
    assert result is False
