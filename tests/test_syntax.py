import pytest
from email_validator_tool.validators.syntax import check
from email_validator_tool.models import ValidationStatus

@pytest.mark.asyncio
async def test_valid_syntax():
    """Test that a valid email passes syntax validation."""
    result = await check("user@example.com")
    assert result.status == ValidationStatus.VALID
    assert result.details is None

@pytest.mark.asyncio
async def test_missing_at_symbol():
    """Test that an email without @ symbol fails validation."""
    result = await check("userexample.com")
    assert result.status == ValidationStatus.INVALID_SYNTAX
    assert "at symbol" in result.details.lower()

@pytest.mark.asyncio
async def test_missing_domain():
    """Test that an email without domain fails validation."""
    result = await check("user@")
    assert result.status == ValidationStatus.INVALID_SYNTAX
    assert "domain" in result.details.lower()

@pytest.mark.asyncio
async def test_invalid_characters():
    """Test that an email with invalid characters fails validation."""
    # Test with spaces
    result = await check("user name@example.com")
    assert result.status == ValidationStatus.INVALID_SYNTAX
    
    # Test with special characters
    result = await check("user*name@example.com")
    assert result.status == ValidationStatus.INVALID_SYNTAX
    
    # Test with multiple @ symbols
    result = await check("user@name@example.com")
    assert result.status == ValidationStatus.INVALID_SYNTAX

@pytest.mark.asyncio
async def test_empty_email():
    """Test that an empty email fails validation."""
    result = await check("")
    assert result.status == ValidationStatus.INVALID_SYNTAX

@pytest.mark.asyncio
async def test_whitespace_only():
    """Test that an email with only whitespace fails validation."""
    result = await check("   ")
    assert result.status == ValidationStatus.INVALID_SYNTAX

@pytest.mark.asyncio
async def test_international_domain():
    """Test that an email with international domain passes validation."""
    result = await check("user@münchen.de")
    assert result.status == ValidationStatus.VALID

@pytest.mark.asyncio
async def test_long_email():
    """Test that a very long email fails validation."""
    long_email = "a" * 64 + "@" + "b" * 255 + ".com"
    result = await check(long_email)
    assert result.status == ValidationStatus.INVALID_SYNTAX
