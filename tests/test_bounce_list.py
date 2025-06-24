"""
Tests for the bounce list validator.
"""

import pytest
from email_validator_tool.validators.bounce_list import BounceListValidator


def test_bounce_list_validator_initialization():
    """Test bounce list validator initialization."""
    validator = BounceListValidator()
    assert validator is not None
    assert validator.name == "bounce_list"


def test_bounce_list_validation(valid_email, validation_result):
    """Test bounce list validation with a valid email."""
    validator = BounceListValidator()
    result = validator.validate(valid_email, validation_result)
    assert isinstance(result, bool)
    assert result is True


def test_bounce_list_validation_with_bounced_email(validation_result):
    """Test bounce list validation with a bounced email."""
    validator = BounceListValidator()
    # Add a test bounced email to the list
    validator.bounce_list.add("bounced@example.com")
    result = validator.validate("bounced@example.com", validation_result)
    assert isinstance(result, bool)
    assert result is False


def test_bounce_list_validation_with_invalid_email(invalid_email, validation_result):
    """Test bounce list validation with an invalid email."""
    validator = BounceListValidator()
    result = validator.validate(invalid_email, validation_result)
    assert isinstance(result, bool)
    assert result is False
