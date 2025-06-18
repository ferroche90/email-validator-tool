"""
Tests for the catch-all email validator.
"""

import pytest
from email_validator_tool.validators.catch_all import CatchAllValidator

def test_catch_all_validator_initialization():
    """Test catch-all validator initialization."""
    validator = CatchAllValidator()
    assert validator is not None
    assert validator.name == "catch_all"

def test_catch_all_validation(valid_email, validation_result):
    """Test catch-all validation with a valid email."""
    validator = CatchAllValidator()
    result = validator.validate(valid_email, validation_result)
    assert isinstance(result, bool)
    assert result is True

def test_catch_all_validation_with_invalid_domain(invalid_email, validation_result):
    """Test catch-all validation with an invalid domain."""
    validator = CatchAllValidator()
    result = validator.validate(invalid_email, validation_result)
    assert isinstance(result, bool)
    assert result is False

def test_catch_all_validation_with_nonexistent_domain(validation_result):
    """Test catch-all validation with a nonexistent domain."""
    validator = CatchAllValidator()
    result = validator.validate("test@nonexistentdomain123456.com", validation_result)
    assert isinstance(result, bool)
    assert result is False
