"""
Tests for the SMTP email validator.
"""

import pytest

from email_validator_tool.validators.smtp import SMTPValidator


def test_smtp_validator_initialization():
    """Test SMTP validator initialization."""
    validator = SMTPValidator()
    assert validator is not None
    assert validator.name == "smtp"


def test_smtp_validation(valid_email, validation_result):
    """Test SMTP validation with a valid email."""
    validator = SMTPValidator()
    result = validator.validate(valid_email, validation_result)
    assert isinstance(result, bool)
    assert result is True


def test_smtp_validation_with_invalid_domain(invalid_email, validation_result):
    """Test SMTP validation with an invalid domain."""
    validator = SMTPValidator()
    result = validator.validate(invalid_email, validation_result)
    assert isinstance(result, bool)
    assert result is False


def test_smtp_validation_with_nonexistent_domain(validation_result):
    """Test SMTP validation with a nonexistent domain."""
    validator = SMTPValidator()
    result = validator.validate("test@nonexistentdomain123456.com", validation_result)
    assert isinstance(result, bool)
    assert result is False


def test_smtp_validation_with_timeout(validation_result):
    """Test SMTP validation with a timeout."""
    validator = SMTPValidator(timeout=0.1)  # Very short timeout
    result = validator.validate("test@example.com", validation_result)
    assert isinstance(result, bool)
    assert result is False


def test_smtp_validation_with_invalid_email(invalid_email, validation_result):
    """Test SMTP validation with an invalid email."""
    validator = SMTPValidator()
    result = validator.validate(invalid_email, validation_result)
    assert isinstance(result, bool)
    assert result is False
