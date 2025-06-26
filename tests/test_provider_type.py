"""Tests for the ProviderTypeValidator."""

import pytest
from email_validator_tool.validators.provider_type import ProviderTypeValidator

@pytest.mark.asyncio
async def test_provider_type_free():
    validator = ProviderTypeValidator()
    result = await validator.validate("foo@gmail.com")
    assert result.meta["free_provider"] is True

@pytest.mark.asyncio
async def test_provider_type_not_free():
    validator = ProviderTypeValidator()
    result = await validator.validate("foo@company.com")
    assert result.meta["free_provider"] is False

@pytest.mark.asyncio
async def test_provider_type_case_insensitive():
    validator = ProviderTypeValidator()
    result = await validator.validate("foo@GMAIL.COM")
    assert result.meta["free_provider"] is True

@pytest.mark.asyncio
async def test_provider_type_invalid_email():
    validator = ProviderTypeValidator()
    result = await validator.validate("invalid-email")
    assert "free_provider" not in result.meta 