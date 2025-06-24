import pytest

from email_validator_tool.core.models import ValidationStatus
from email_validator_tool.validators.syntax import SyntaxValidator


@pytest.mark.asyncio
async def test_valid_syntax():
    """Test that a valid email passes syntax validation."""
    validator = SyntaxValidator()
    result = await validator.validate("user@example.com")
    assert result.status in [ValidationStatus.VALID, ValidationStatus.INVALID_DOMAIN]


@pytest.mark.asyncio
async def test_missing_at_symbol():
    """Test that an email without @ symbol fails validation."""
    validator = SyntaxValidator()
    result = await validator.validate("userexample.com")
    assert result.status == ValidationStatus.INVALID_SYNTAX
    assert "@-sign" in result.details.lower()


@pytest.mark.asyncio
async def test_missing_domain():
    """Test that an email without domain fails validation."""
    validator = SyntaxValidator()
    result = await validator.validate("user@")
    assert result.status == ValidationStatus.INVALID_SYNTAX
    assert "after the @-sign" in result.details.lower()


@pytest.mark.asyncio
async def test_invalid_characters():
    """Test that an email with invalid characters fails validation."""
    validator = SyntaxValidator()
    # Test with spaces
    result = await validator.validate("user name@example.com")
    assert result.status == ValidationStatus.INVALID_SYNTAX

    # Test with special characters
    result = await validator.validate("user*name@example.com")
    assert result.status in [ValidationStatus.INVALID_SYNTAX, ValidationStatus.INVALID_DOMAIN]

    # Test with multiple @ symbols
    result = await validator.validate("user@name@example.com")
    assert result.status == ValidationStatus.INVALID_SYNTAX


@pytest.mark.asyncio
async def test_empty_email():
    """Test that an empty email fails validation."""
    validator = SyntaxValidator()
    result = await validator.validate("")
    assert result.status == ValidationStatus.INVALID_SYNTAX


@pytest.mark.asyncio
async def test_whitespace_only():
    """Test that an email with only whitespace fails validation."""
    validator = SyntaxValidator()
    result = await validator.validate("   ")
    assert result.status == ValidationStatus.INVALID_SYNTAX


@pytest.mark.asyncio
async def test_international_domain():
    """Test that an email with international domain passes validation."""
    validator = SyntaxValidator()
    result = await validator.validate("user@münchen.de")
    assert result.status == ValidationStatus.VALID


@pytest.mark.asyncio
async def test_long_email():
    """Test that a very long email fails validation."""
    validator = SyntaxValidator()
    long_email = "a" * 64 + "@" + "b" * 255 + ".com"
    result = await validator.validate(long_email)
    assert result.status == ValidationStatus.INVALID_SYNTAX
